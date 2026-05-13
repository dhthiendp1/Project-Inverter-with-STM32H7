#pragma once
#include <zmq.hpp>
#include <string>
#include <memory>
#include "Core/DataPacket.hpp"

namespace FOC {
    namespace IPC {

        class ZmqPublisher {
        public:
            // Cổng mặc định giao tiếp với Python (ví dụ: tcp://127.0.0.1:5555)
            ZmqPublisher(const std::string& address = "tcp://127.0.0.1:5555");
            ~ZmqPublisher();

            // Khởi tạo kết nối
            bool initialize();

            // Bắn dữ liệu sang Python
            bool publishData(const Core::DataFrame& frame);

            // Gửi thông điệp điều khiển (VD: "CONNECTED", "OFFLINE")
            bool publishStatus(const std::string& status_msg);

        private:
            std::string address_;
            std::unique_ptr<zmq::context_t> context_;
            std::unique_ptr<zmq::socket_t> publisher_;
        };

    } // namespace IPC
} // namespace FOC