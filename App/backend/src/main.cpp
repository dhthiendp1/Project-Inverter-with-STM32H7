#include <iostream>
#include <thread>
#include <chrono>
#include <fstream>
#include <nlohmann/json.hpp>
#include "IPC/ZmqPublisher.hpp"
#include "Hardware/StlinkReader.hpp"

using json = nlohmann::json;

// Hàm hỗ trợ đọc file mapping của Python tạo ra
std::vector<FOC::Core::VariableConfig> loadVariablesFromJson(const std::string& filepath) {
    std::vector<FOC::Core::VariableConfig> vars;
    std::ifstream f(filepath);
    if (!f.is_open()) return vars;

    json data = json::parse(f);
    for (auto& [block_name, var_list] : data.items()) {
        for (auto& v : var_list) {
            FOC::Core::VariableConfig cfg;
            cfg.name = v["id"];
            cfg.address = std::stoul(v["addr"].get<std::string>(), nullptr, 16); // Hex string to uint32
            cfg.type = v["type"];
            vars.push_back(cfg);
        }
    }
    return vars;
}

int main() {
    std::cout << "=== FOC SYSTEM ARCHITECT BACKEND (C++) ===" << std::endl;

    FOC::IPC::ZmqPublisher zmq_pub("tcp://127.0.0.1:5555");
    if (!zmq_pub.initialize()) return -1;

    FOC::Hardware::StlinkReader stlink;

    // Liên tục thử kết nối cho đến khi cắm cáp
    while (!stlink.connect()) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    // Đọc file config (Phải chạy Frontend Python trước để tạo file này)
    auto vars = loadVariablesFromJson("../frontend/block_mapping.json");
    stlink.setTargetVariables(vars);

    std::cout << "Bat dau stream du lieu... Nhấn Ctrl+C de dung." << std::endl;

    auto start_time = std::chrono::high_resolution_clock::now();

    // Vòng lặp Real-time
    while (true) {
        auto current_time = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = current_time - start_time;

        // Đọc dữ liệu từ RAM STM32
        FOC::Core::DataFrame frame = stlink.readFrame();
        frame.timestamp = elapsed.count();

        // Bắn sang Python
        zmq_pub.publishData(frame);

        // Chạy ở tốc độ ~1kHz (1ms) - Có thể giảm xuống microseconds nếu ZMQ cấu hình tốt
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }

    return 0;
}