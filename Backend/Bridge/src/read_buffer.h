#pragma once

#include <Arduino.h>

class ReadBuffer {
    public:
        ReadBuffer(uint8_t buffer_size);
        void clean();
        void append(const char input_byte);
        const char* read();

    private:
        char* read_buffer;
        uint8_t read_buffer_size;
        uint8_t read_buffer_index;
};