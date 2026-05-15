#pragma once
#include <zmq.hpp>
#include <string>
#include "DataPacket.hpp"

namespace FOC {
    class ZmqPublisher {
    public:
        ZmqPublisher(const std::string& addr);
        bool init();
        void sendData(const DataFrame& frame);
    private:
        zmq::context_t context;
        zmq::socket_t publisher;
        std::string address;
    };
}