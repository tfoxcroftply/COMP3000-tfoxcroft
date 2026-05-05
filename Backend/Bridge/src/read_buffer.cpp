// used in bridge and nodes

#include "read_buffer.h"

#include <Arduino.h>

ReadBuffer::ReadBuffer(uint16_t buffer_size) {
    read_buffer_size = buffer_size;
    read_buffer = new char[read_buffer_size];
    clean();
};

void ReadBuffer::clean() {
    // clean buffer (just puts the end marker at the front)
    read_buffer_index = 0;
    read_buffer[0] = '\0';
}

// update read buffer
void ReadBuffer::append(const char input_byte) {
    if (input_byte == '\0') { return; }

    // shift bytes left if buffer is already full
    if (read_buffer_index >= read_buffer_size - 1) {
        memmove(read_buffer, read_buffer + 1, read_buffer_size - 2); // fixed memory corruption
        read_buffer_index--;
    }

    // append new byte to buffer
    read_buffer[read_buffer_index++] = input_byte;
    read_buffer[read_buffer_index] = '\0';
}

const char* ReadBuffer::read() {
    // return buffer (encapsulated)
    return read_buffer;
}

