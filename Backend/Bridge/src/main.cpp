// bridge
// lora <-> server

#include "display_class.h"
#include "bridge.h"
#include "constants.h"

#include <Arduino.h>
#include <RadioLib.h>
#include <string>

SX1276 radio = new Module(LORA_CS, LORA_IRQ, LORA_RST, -1);
Bridge bridge;
DisplayClass display;
uint8_t received_buffer[255];

void setup() {
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);

    display.setup();
    display.print("Starting bridge.");

    delay(1000); // wait for lora to start properly

    int state;
    while (true) {
        state = radio.begin(868.0);
        if (state == RADIOLIB_ERR_NONE) { break; }

        display.print("LoRa module failed to connect. Retrying.");
        delay(5000);  // wait until valid
    }

    display.print("LoRa module initialised successfully.");
    radio.setOutputPower(LORA_POWER);

    display.print("Connecting to server.");
    bridge.display = &display;
    bridge.setup();
    display.print("Server connected successfully.");
}

void loop() {
    display.update();
    bridge.ping(); // delete later, let bridge module handle it if input is "tnh:ping:""

    memset(received_buffer, 0, sizeof(received_buffer));
    const uint16_t radio_state = radio.receive(received_buffer, sizeof(received_buffer));

    if (radio_state == RADIOLIB_ERR_NONE) {
        const size_t packet_length = radio.getPacketLength();
        const bool sent = bridge.send(received_buffer, packet_length);
    }

    const char test[] = "tnn:111111111111:t-20h50b30"; // incoming lora commands should be in this format, perhaps change optional negative to 0 as in t020h
    bridge.send((const uint8_t*)test, strlen(test));

    delay(20000);
}