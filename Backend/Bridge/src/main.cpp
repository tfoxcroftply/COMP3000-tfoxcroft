// bridge
// lora <-> server

#include "display_class.h"
#include "bridge.h"
#include "constants.h"

#include <Arduino.h>
#include <RadioLib.h>
#include <string>

SX1276 radio = new Module(LORA_CS, LORA_IRQ, LORA_RST, -1);
char received_buffer[256]; // 256 instead of 255. lora uses full 255 and needs a null terminator

Bridge bridge(sizeof(received_buffer));
DisplayClass display;
volatile bool data_received = false;

void receive_callback() {
    data_received = true;
}

void setup() {
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);

    display.setup();
    display.print("Starting bridge.");

    pinMode(LED_PIN, OUTPUT);

    delay(1000); // wait for lora to start properly

    int state;
    while (true) {
        state = radio.begin(868.0, LORA_BW, LORA_SF, LORA_CR);
        if (state == RADIOLIB_ERR_NONE) { break; }

        display.print("LoRa module failed to connect. Retrying.");
        delay(5000);  // wait until valid
    }

    display.print("LoRa module initialised successfully.");
    display.print("Connecting to server.");
    bridge.setup();

    display.update();

    radio.setOutputPower(LORA_POWER);
    radio.setDio0Action(receive_callback, RISING);
    radio.startReceive();

    //display.print("Server connected successfully.");
}

void loop() {
    if (data_received == true) {
        data_received = false;

        if (DEBUG_MODE) {
            digitalWrite(LED_PIN, HIGH);
            delay(50);
            digitalWrite(LED_PIN, LOW);
        }

        display.update();

        const size_t packet_length = radio.getPacketLength();
        radio.readData((uint8_t*)received_buffer, packet_length);
        received_buffer[packet_length] = '\0';

        const bool sent = bridge.send(received_buffer, packet_length + 1); // basic validation in bridge.send()

        radio.startReceive();
    }

    //delay(50); // lora commands will likely be 200ms each, needs to check often
}