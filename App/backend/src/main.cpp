#include <iostream>
#include <thread>
#include <chrono>
#include <fstream>
#include <cmath>
#include <nlohmann/json.hpp>
#include "StlinkReader.hpp"
#include "ZmqPublisher.hpp"
#include <filesystem>

using json = nlohmann::json;

int main() {
    std::cout << "=== FOC SYSTEM BACKEND (MOCK MODE) ===" << std::endl;

    FOC::StlinkReader reader;
    FOC::ZmqPublisher pub("tcp://127.0.0.1:5556");

    if (!reader.connect() || !pub.init()) {
        std::cerr << "Initialization Failed!" << std::endl;
        return -1;
    }

    std::vector<FOC::VariableConfig> active_vars;

    // --- BẮT C++ IN RA THƯ MỤC NÓ ĐANG TÌM FILE ---
    std::cout << "\n==============================================" << std::endl;
    std::cout << "[QUAN TRONG] C++ dang tim file JSON tai thu muc:" << std::endl;
    std::cout << " ---> " << std::filesystem::current_path() << std::endl;
    std::cout << "==============================================\n" << std::endl;

    std::ifstream f("block_mapping.json");
    if (f.is_open()) {
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
        std::cout << "[Backend] Thanh cong! Da load " << active_vars.size() << " bien de gui di." << std::endl;
    }
    else {
        std::cerr << "[LOI] KHONG TIM THAY FILE block_mapping.json!" << std::endl;
    }

    zmq::context_t cmd_ctx(1);
    zmq::socket_t cmd_sub(cmd_ctx, zmq::socket_type::sub);
    cmd_sub.connect("tcp://127.0.0.1:5557");
    cmd_sub.set(zmq::sockopt::subscribe, "WRITE");

    auto start_time = std::chrono::high_resolution_clock::now();

    while (true) {
        zmq::message_t topic;
        auto res_topic = cmd_sub.recv(topic, zmq::recv_flags::dontwait);

        if (res_topic.has_value()) {

            if (!topic.more()) continue;

            zmq::message_t payload;
            auto res_payload = cmd_sub.recv(payload, zmq::recv_flags::none);

            if (res_payload.has_value()) {
                try {
                    auto j = json::parse(payload.to_string());
                    uint32_t addr = std::stoul(j["addr"].get<std::string>(), nullptr, 16);
                    std::string val_str = j["val_str"].get<std::string>();
                    std::string type = j["type"].get<std::string>(); // Lấy thêm Data Type

                    if (reader.writeMemory(addr, val_str, type)) {
                        std::cout << "[Backend] GHI THANH CONG: " << val_str << " (" << type << ") vao " << std::hex << addr << std::endl;
                    }
                }
                catch (const std::exception& e) {
                    std::cerr << "[Backend] Loi Parse JSON: " << e.what() << std::endl;
                }
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