#pragma once

#include "constants.h"

#include <Arduino.h>

class USB_Mode {
    public:
        void setup(uint8_t timeout = 10);
        bool is_connected();
 
    private:
        class Read_Buffer {
            public:
                Read_Buffer();
                void update(char input_byte);
                bool has(const char* input_buffer);
                const char* read();
                void clear();
            private:
                bool has_run = false;
                char read_buffer[SERIAL_BUFFER_SIZE];
                uint8_t read_buffer_index;
        };

        void main();
        void handle_command(const char* input_buffer);

        Read_Buffer read_buffer;
        bool connected = false;
        bool busy = false;
        bool started = false;


};
