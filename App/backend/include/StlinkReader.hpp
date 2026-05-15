#pragma once
#include <stlink.h>
#include <string>
#include <cstdint>

namespace FOC {
    class StlinkReader {
    public:
        StlinkReader();
        ~StlinkReader();
        bool connect();
        void disconnect();
        float readMemory(uint32_t addr, const std::string& type);
        bool writeMemory(uint32_t addr, const std::string& val_str, const std::string& type);

    private:
        stlink_t* sl = nullptr;
        bool is_connected = false;
    };
}