#pragma once
#include <vector>
#include <string>
#include "Core/DataPacket.hpp"

namespace FOC {
    namespace Hardware {

        class StlinkReader {
        public:
            StlinkReader();
            ~StlinkReader();

            // Kết nối vào cáp ST-Link
            bool connect();
            void disconnect();

            // Cập nhật danh sách các biến cần đọc (Lấy từ block_mapping.json)
            void setTargetVariables(const std::vector<Core::VariableConfig>& vars);

            // Đọc 1 Frame dữ liệu (thực thi hàm này trong vòng lặp 20kHz)
            Core::DataFrame readFrame();

        private:
            bool is_connected_;
            std::vector<Core::VariableConfig> target_vars_;

            // TODO: Thêm con trỏ tới thư viện libstlink (stlink_t* stl) ở đây
            // void* stlink_handle_; 

            // Hàm tiện ích đọc bộ nhớ
            float readFloat32(uint32_t address);
            int32_t readInt32(uint32_t address);
        };

    } // namespace Hardware
} // namespace FOC