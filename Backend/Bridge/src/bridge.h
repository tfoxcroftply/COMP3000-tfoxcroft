#pragma once

#include "constants.h"
#include "display_class.h"

#include <Arduino.h>

class Bridge {
    public:
        Bridge() {};
        void setup();
        bool is_connected();
        bool send(const uint8_t* data_buffer, const size_t buffer_size);
        void ping();
        DisplayClass *display;
    private:
        void loop();
        bool connected = false;
};