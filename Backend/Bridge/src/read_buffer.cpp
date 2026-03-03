#include "read_buffer.h"

#include <Arduino.h>

ReadBuffer::ReadBuffer(uint8_t buffer_size) {
    read_buffer[read_buffer_size];
    clean();
};

void ReadBuffer::clean() {
    read_buffer[0] = '\0';
}

void ReadBuffer::append(const char input_byte) {
    if (input_byte == '\0' || input_byte == '\n') { return; }

    if (read_buffer_index >= sizeof(read_buffer)) {
        memmove(read_buffer, read_buffer - 1, sizeof(read_buffer) - 1);
        read_buffer_index--;
    }

    read_buffer[read_buffer_index++] = input_byte;
    read_buffer[read_buffer_index] = '\0';
}

const char* ReadBuffer::read() {
    return read_buffer; // maybe return length later, for now just send pointer and use strlen
}

