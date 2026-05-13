#include "IPC/ZmqPublisher.hpp"
#include <nlohmann/json.hpp>
#include <iostream>

namespace FOC {
    namespace IPC {

        ZmqPublisher::ZmqPublisher(const std::string& address) : address_(address) {
            // Khởi tạo Context và Socket loại PUB (Publisher)
            context_ = std::make_unique<zmq::context_t>(1);
            publisher_ = std::make_unique<zmq::socket_t>(*context_, zmq::socket_type::pub);
        }

        ZmqPublisher::~ZmqPublisher() {
            publisher_->close();
        }

        bool ZmqPublisher::initialize() {
            try {
                publisher_->bind(address_);
                std::cout << "[ZMQ] Đã mở cổng tại: " << address_ << std::endl;
                return true;
            }
            catch (const zmq::error_t& e) {
                std::cerr << "[ZMQ Lỗi] Không thể bind: " << e.what() << std::endl;
                return false;
            }
        }

        bool ZmqPublisher::publishData(const Core::DataFrame& frame) {
            nlohmann::json j;
            j["timestamp"] = frame.timestamp;
            j["values"] = frame.values; // Mảng các giá trị float

            std::string payload = j.dump();
            zmq::message_t message(payload.size());
            memcpy(message.data(), payload.data(), payload.size());

            // Gắn topic "DATA" ở đầu để Python dễ lọc
            publisher_->send(zmq::message_t("DATA", 4), zmq::send_flags::sndmore);
            return publisher_->send(message, zmq::send_flags::none).has_value();
        }

    } // namespace IPC
} // namespace FOC