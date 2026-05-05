#pragma once

#include "constants.h"

#include "display_class.h"
#include "read_buffer.h"

#include <Arduino.h>

class Bridge {
    public:
        Bridge(uint16_t read_buffer_size);
        void setup();
        bool send(const char* data_buffer, const size_t buffer_size);
        void ping();
    private:
        void loop();
        bool connected = false;
        DisplayClass* display;
        ReadBuffer read_buffer;
};