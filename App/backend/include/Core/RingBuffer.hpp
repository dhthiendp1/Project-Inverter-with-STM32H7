#pragma once
#include <vector>
#include <mutex>
#include <optional>

namespace FOC {
    namespace Core {

        template <typename T>
        class RingBuffer {
        public:
            explicit RingBuffer(size_t capacity);

            bool push(const T& item);
            std::optional<T> pop();

            size_t size() const;
            bool isEmpty() const;
            bool isFull() const;

        private:
            std::vector<T> buffer_;
            size_t head_;
            size_t tail_;
            size_t max_size_;
            bool full_;
            mutable std::mutex mutex_;
        };

    } // namespace Core
} // namespace FOC