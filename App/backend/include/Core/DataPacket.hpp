#pragma once
#include <vector>
#include <string>
#include <cstdint>

namespace FOC {
    namespace Core {

        // Cấu trúc một khung hình dữ liệu tại 1 thời điểm
        struct DataFrame {
            double timestamp;           // Thời gian lấy mẫu (giây)
            std::vector<float> values;  // Mảng chứa các giá trị (I_a, I_b, Speed...)
        };

        // Thông tin cấu hình đọc từ JSON của Python
        struct VariableConfig {
            std::string name;
            uint32_t address;
            std::string type;
        };

    } // namespace Core
} // namespace FOC