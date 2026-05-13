#include "Hardware/StlinkReader.hpp"
#include <stlink.h>
#include <iostream>
#include <cstring>

namespace FOC {
    namespace Hardware {

        StlinkReader::StlinkReader() : is_connected_(false), stlink_handle_(nullptr) {}

        StlinkReader::~StlinkReader() {
            disconnect();
        }

        bool StlinkReader::connect() {
            // Kết nối với thiết bị ST-Link đầu tiên tìm thấy qua USB
            stlink_t* sl = stlink_open_usb(0, 1, NULL);
            if (sl == NULL) {
                std::cerr << "[ST-Link] Lỗi: Không tìm thấy cáp ST-Link!" << std::endl;
                return false;
            }

            // Vào chế độ SWD
            if (stlink_enter_swd_mode(sl) != 0) {
                std::cerr << "[ST-Link] Lỗi: Không thể vào chế độ SWD!" << std::endl;
                stlink_close(sl);
                return false;
            }

            stlink_handle_ = sl;
            is_connected_ = true;
            std::cout << "[ST-Link] Đã kết nối thành công với MCU!" << std::endl;
            return true;
        }

        void StlinkReader::disconnect() {
            if (is_connected_ && stlink_handle_ != nullptr) {
                stlink_t* sl = static_cast<stlink_t*>(stlink_handle_);
                stlink_exit_debug_mode(sl);
                stlink_close(sl);
                stlink_handle_ = nullptr;
                is_connected_ = false;
                std::cout << "[ST-Link] Đã ngắt kết nối." << std::endl;
            }
        }

        void StlinkReader::setTargetVariables(const std::vector<Core::VariableConfig>& vars) {
            target_vars_ = vars;
        }

        Core::DataFrame StlinkReader::readFrame() {
            Core::DataFrame frame;
            frame.timestamp = 0.0; // Sẽ được gán ở hàm main

            if (!is_connected_) return frame;

            stlink_t* sl = static_cast<stlink_t*>(stlink_handle_);

            // Duyệt qua từng biến cần đọc
            for (const auto& var : target_vars_) {
                // Đọc 4 bytes từ địa chỉ RAM
                stlink_read_mem32(sl, var.address, 4);

                // sl->q_buf chứa dữ liệu trả về từ MCU
                float value = 0.0f;
                if (var.type == "float32") {
                    memcpy(&value, sl->q_buf, 4);
                }
                else if (var.type == "int32") {
                    int32_t int_val;
                    memcpy(&int_val, sl->q_buf, 4);
                    value = static_cast<float>(int_val);
                }
                // ... (Có thể mở rộng thêm uint16, uint8 tại đây) ...

                frame.values.push_back(value);
            }
            return frame;
        }

    } // namespace Hardware
} // namespace FOC