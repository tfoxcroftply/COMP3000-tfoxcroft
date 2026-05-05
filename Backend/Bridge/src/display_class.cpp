#include "display_class.h"

#include "constants.h"

#include <Arduino.h>
#include <Adafruit_SSD1306.h>

DisplayClass::DisplayClass() : display(DISPLAY_X, DISPLAY_Y, &Wire, OLED_RST) {}

void DisplayClass::setup() {
    if (running) { return; }
    running = true;

    Wire.begin(OLED_SDA, OLED_SCL);
    display.begin(SSD1306_SWITCHCAPVCC, 0x3C);

    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.setTextWrap(true);
    display.setRotation(2);
    display.clearDisplay();
    display.display();
}


void DisplayClass::print(const char buffer[]) {
    if (!setup_mode) { return; }

    // add logic to shift lines up later

    display.println(buffer);
    display.display();
}

void DisplayClass::clear() {
    display.clearDisplay();
    display.setCursor(0, 0);
    display.display();
}

void DisplayClass::update() {
    if (setup_mode) {
        setup_mode = false;
        display.clearDisplay();
    }

    display.clearDisplay();

    display.setCursor(0, 0);
    display.setTextSize(2);
    display.write("TN Server\n\n");
    
    //display.setTextSize(1);
    //display.write("Connected devices: 0\n");  // placeholders
    //display.write("Last update: 12:00\n");
    //display.write("CPU temperature: ?c");

    display.display();
}


