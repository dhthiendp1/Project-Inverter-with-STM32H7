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

    auto start_time = std::chrono::high_resolution_clock::now();

    while (true) {
        auto now = std::chrono::high_resolution_clock::now();
        double elapsed = std::chrono::duration<double>(now - start_time).count();

        FOC::DataFrame frame;
        frame.timestamp = elapsed;

        for (auto& var : active_vars) {
            float val = reader.readMemory(var.address, var.type);
            //val += static_cast<float>(sin(elapsed * 5.0 + var.address)) * 2.0f;
            frame.data[var.id] = val;
        }

        pub.sendData(frame);
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    return 0;
}