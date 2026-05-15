#pragma once
#include <map>
#include <string>
#include <cstdint>

namespace FOC {
    struct VariableConfig {
        std::string id;
        uint32_t address;
        std::string type;
    };

    struct DataFrame {
        double timestamp;
        std::map<std::string, float> data;
    };
}