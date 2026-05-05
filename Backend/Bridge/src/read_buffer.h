#pragma once

#include <Arduino.h>

class ReadBuffer {
    public:
        ReadBuffer(uint16_t buffer_size);
        void clean();
        void append(const char input_byte);
        const char* read();

    private:
        char* read_buffer;
        uint16_t read_buffer_size;
        uint16_t read_buffer_index = 0;
};