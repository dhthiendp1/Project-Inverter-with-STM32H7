#pragma once
#include <stlink.h>
#include <string>
#include <cstdint>

namespace FOC {
    class StlinkReader {
    public:
        StlinkReader();
        ~StlinkReader();

        // Kết nối với ST-Link qua cổng USB
        bool connect();

        // Ngắt kết nối và giải phóng tài nguyên
        void disconnect();

        // Đọc giá trị từ một địa chỉ RAM cụ thể
        float readMemory(uint32_t addr, const std::string& type);

    private:
        stlink_t* sl = nullptr; // Cấu trúc quản lý thiết bị của thư viện stlink
        bool is_connected = false;
    };
}