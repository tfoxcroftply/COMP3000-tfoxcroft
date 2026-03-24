#include "read_buffer.h"

#include <Arduino.h>
#include <cstring>

ReadBuffer::ReadBuffer(uint8_t buffer_size) {
    read_buffer_size = buffer_size;
    read_buffer = new char[read_buffer_size + 1];
    clear();
};

void ReadBuffer::clear() {
    read_buffer_index = 0;
    read_buffer[0] = '\0';
}

void ReadBuffer::append(const char input_byte) {
    if (input_byte == '\0') { return; }

    if (read_buffer_index >= read_buffer_size - 1) {
        memmove(read_buffer, read_buffer + 1, read_buffer_size - 2); // fixed memory corruption
        read_buffer_index--;
    }

    read_buffer[read_buffer_index++] = input_byte;
    read_buffer[read_buffer_index] = '\0';
}

const char* ReadBuffer::read() {
    return read_buffer; // maybe return length later, for now just send pointer and use strlen
}

bool ReadBuffer::has(const char* input_buffer) {
    return std::strstr(read_buffer, input_buffer) != nullptr;
}
