#pragma once

#include "constants.h"
#include "read_buffer.h"
#include "display_class.h"

#include <Arduino.h>
#include <cstring>

class USBMode {
    public:
        USBMode(DisplayClass* input_display);
        bool start();

    private:
        bool handle_command();
        void send_pair_command();

        ReadBuffer read_buffer;
        DisplayClass* display;

        bool running = false;
        bool hasRun = false;
        bool paired = false;
};
