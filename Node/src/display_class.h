#pragma once

#include "constants.h"

#include <Arduino.h>
#include <Adafruit_SSD1306.h>

class DisplayClass {
    public:
        DisplayClass();
        void setup();
        void end();
        void print(const char buffer[]);
        void clear();

    private:
        Adafruit_SSD1306 display;
        bool running = false;
        bool setup_mode = true;
};