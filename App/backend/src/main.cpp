#include <iostream>
#include <thread>
#include <chrono>
#include <fstream>
#include <cmath>
#include <nlohmann/json.hpp>
#include "StlinkReader.hpp"
#include "ZmqPublisher.hpp"
#include <filesystem>
#include <zmq.hpp>

using json = nlohmann::json;

// --- HÀM TỰ ĐỘNG ĐỌC CẤU HÌNH BIẾN ---
void loadConfiguration(const std::string& path, std::vector<FOC::VariableConfig>& active_vars) {
    std::ifstream f(path);
    if (f.is_open()) {
        active_vars.clear(); // Xóa sạch danh sách biến cũ trong RAM C++
        json data = json::parse(f);
        for (auto& [block, vars] : data.items()) {
            for (auto& v : vars) {
                active_vars.push_back({
                    v["id"],
                    std::stoul(v["addr"].get<std::string>(), nullptr, 16),
                    v["type"]
                    });
            }
        }
        std::cout << "\n[Backend] ---> HOT-RELOAD SUCCESS! Da cap nhat " << active_vars.size() << " bien tu file JSON moi." << std::endl;
    }
    else {
        std::cerr << "\n[Backend] [LOI] Khong the doc file JSON tai: " << path << std::endl;
    }
}

int main() {
    std::cout << "=== FOC SYSTEM BACKEND (ST-LINK & ZMQ) ===" << std::endl;

    FOC::StlinkReader reader;
    FOC::ZmqPublisher pub("tcp://127.0.0.1:5556");

    if (!reader.connect() || !pub.init()) {
        std::cerr << "Initialization Failed!" << std::endl;
        return -1;
    }

    std::vector<FOC::VariableConfig> active_vars;

    std::string config_path = FRONTEND_JSON_PATH;

    // Nạp cấu hình lần đầu lúc khởi động
    loadConfiguration(config_path, active_vars);
    // Kênh nhận lệnh từ Python (Cổng 5557)
    zmq::context_t cmd_ctx(1);
    zmq::socket_t cmd_sub(cmd_ctx, zmq::socket_type::sub);
    cmd_sub.connect("tcp://127.0.0.1:5557");
    cmd_sub.set(zmq::sockopt::subscribe, "WRITE");
    cmd_sub.set(zmq::sockopt::subscribe, "RELOAD"); // Đăng ký nhận thêm tín hiệu làm tươi bộ nhớ

    auto start_time = std::chrono::high_resolution_clock::now();

    while (true) {
        zmq::message_t topic;
        auto res_topic = cmd_sub.recv(topic, zmq::recv_flags::dontwait);

        if (res_topic.has_value()) {
            std::string topic_str = topic.to_string();

            if (topic_str == "WRITE" && topic.more()) {
                zmq::message_t payload;
                auto res_payload = cmd_sub.recv(payload, zmq::recv_flags::none);
                if (res_payload.has_value()) {
                    try {
                        auto j = json::parse(payload.to_string());
                        uint32_t addr = std::stoul(j["addr"].get<std::string>(), nullptr, 16);
                        std::string val_str = j["val_str"].get<std::string>();
                        std::string type = j["type"].get<std::string>();

                        if (reader.writeMemory(addr, val_str, type)) {
                            std::cout << "[Backend] WRITE SUCCESS: " << val_str << " (" << type << ") to " << std::hex << addr << std::endl;
                        }
                    }
                    catch (const std::exception& e) {
                        std::cerr << "[Backend] Loi Parse JSON khi ghi: " << e.what() << std::endl;
                    }
                }
            }
            else if (topic_str == "RELOAD") {
                loadConfiguration(config_path, active_vars);
            }
        }
        auto now = std::chrono::high_resolution_clock::now();
        double elapsed = std::chrono::duration<double>(now - start_time).count();

        FOC::DataFrame frame;
        frame.timestamp = elapsed;

        for (auto& var : active_vars) {
            float val = reader.readMemory(var.address, var.type);
            frame.data[var.id] = val;
        }

        pub.sendData(frame);
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    return 0;
}