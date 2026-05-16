#include "StlinkReader.hpp"
#include <iostream>
#include <cstring>

namespace FOC {

    StlinkReader::StlinkReader() : sl(nullptr), is_connected(false) {}

    StlinkReader::~StlinkReader() {
        disconnect();
    }

    bool StlinkReader::connect() {
        std::cout << "[Hardware] Dang quet tim thiet bi ST-Link..." << std::endl;

        sl = stlink_open_usb(UINFO, CONNECT_NORMAL, NULL, 0);

        if (sl == NULL) {
            std::cerr << "[Hardware] LOI: Khong tim thay cap nap ST-Link!" << std::endl;
            return false;
        }

        // Thiết lập chế độ SWD (Serial Wire Debug)
        if (stlink_enter_swd_mode(sl) != 0) {
            std::cerr << "[Hardware] LOI: Khong the vao che do SWD!" << std::endl;
            stlink_close(sl);
            sl = nullptr;
            return false;
        }

        is_connected = true;
        std::cout << "[Hardware] KET NOI THANH CONG: STM32H7 thuc te da san sang." << std::endl;
        return true;
    }

    void StlinkReader::disconnect() {
        if (sl != nullptr) {
            stlink_exit_debug_mode(sl);
            stlink_close(sl);
            sl = nullptr;
            is_connected = false;
            std::cout << "[Hardware] Da ngat ket noi voi thiet bi." << std::endl;
        }
    }

    float StlinkReader::readMemory(uint32_t addr, const std::string& type) {
        if (!is_connected || sl == nullptr) return 0.0f;

        if (stlink_read_mem32(sl, addr, 4) != 0) {
            return 0.0f;
        }

        if (type == "float32") {
            float val;
            std::memcpy(&val, sl->q_buf, 4);
            return val;
        }
        else if (type == "uint8") {
            uint8_t val;
            std::memcpy(&val, sl->q_buf, 1);
            return static_cast<float>(val);
        }
        else if (type == "int8") {
            int8_t val;
            std::memcpy(&val, sl->q_buf, 1);
            return static_cast<float>(val);
        }
        else if (type == "uint16") {
            uint16_t val;
            std::memcpy(&val, sl->q_buf, 2);
            return static_cast<float>(val);
        }
        else if (type == "int16") {
            int16_t val;
            std::memcpy(&val, sl->q_buf, 2);
            return static_cast<float>(val);
        }
        else if (type == "uint32") {
            uint32_t val;
            std::memcpy(&val, sl->q_buf, 4);
            return static_cast<float>(val);
        }
        else { // Mặc định là int32
            int32_t val;
            std::memcpy(&val, sl->q_buf, 4);
            return static_cast<float>(val);
        }
    }

    bool StlinkReader::writeMemory(uint32_t addr, const std::string& val_str, const std::string& type) {
        if (!is_connected || sl == nullptr) return false;

        try {
            if (type == "float32") {
                float val = std::stof(val_str);
                std::memcpy(sl->q_buf, &val, 4);
                return (stlink_write_mem32(sl, addr, 4) == 0);
            }
            else if (type == "uint8" || type == "int8") {
                uint8_t val = static_cast<uint8_t>(std::stoi(val_str));
                std::memcpy(sl->q_buf, &val, 1);
                return (stlink_write_mem8(sl, addr, 1) == 0);
            }
            else if (type == "int16" || type == "uint16") {
                uint16_t val = static_cast<uint16_t>(std::stoi(val_str));
                std::memcpy(sl->q_buf, &val, 2);
                return (stlink_write_mem8(sl, addr, 2) == 0);
            }
            else { // int32 / uint32
                uint32_t val = static_cast<uint32_t>(std::stoul(val_str));
                std::memcpy(sl->q_buf, &val, 4);
                return (stlink_write_mem32(sl, addr, 4) == 0);
            }
        }
        catch (...) {
            std::cerr << "[Hardware] Loi ep kieu du lieu khi ghi!" << std::endl;
            return false;
        }
    }

} // namespace FOC