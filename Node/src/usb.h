#pragma once

#include "constants.h"

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
                uint read_buffer_index;
        };

        Read_Buffer read_buffer;
        bool connected = false;
        bool busy = false;
        bool started = false;

        void main();
        void handle_command(const char* input_buffer);
};
