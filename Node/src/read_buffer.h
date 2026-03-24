#pragma once

#include <Arduino.h>
#include <cstring>

class ReadBuffer {
    public:
        ReadBuffer(uint8_t buffer_size);
        void clear();
        void append(const char input_byte);
        const char* read();
        bool has(const char* input_buffer);

    private:
        char* read_buffer;
        uint8_t read_buffer_size;
        uint8_t read_buffer_index = 0;
};