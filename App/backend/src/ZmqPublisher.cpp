#include "ZmqPublisher.hpp"
#include <nlohmann/json.hpp>
#include <iostream>

namespace FOC {
    ZmqPublisher::ZmqPublisher(const std::string& addr)
        : context(1), publisher(context, zmq::socket_type::pub), address(addr) {
    }

    bool ZmqPublisher::init() {
        try {
            publisher.bind(address);
            std::cout << "[ZMQ] Server bound to " << address << std::endl;
            return true;
        }
        catch (...) {
            return false;
        }
    }

    void ZmqPublisher::sendData(const DataFrame& frame) {
        nlohmann::json j;
        j["timestamp"] = frame.timestamp;
        j["data"] = frame.data; // SỬA DÒNG NÀY (nlohmann tự động hiểu std::map)

        std::string payload = j.dump();
        publisher.send(zmq::str_buffer("DATA"), zmq::send_flags::sndmore);
        publisher.send(zmq::buffer(payload), zmq::send_flags::none);
    }
}