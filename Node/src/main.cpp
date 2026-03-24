// rewrite

#include "constants.h"

#include "display_class.h"
#include "usb.h"

#include <Arduino.h>
#include <Preferences.h>
#include <DHT.h>
#include <RadioLib.h>

#define DHT_TYPE DHT22

SX1276 radio = new Module(LORA_CS, LORA_IRQ, LORA_RST, -1);
DisplayClass display;
USBMode* usb_mode = nullptr; // pointer temporary
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
    dht.begin(); // may need to reinitialise after sleep, test later
    display.setup();

    usb_mode = new USBMode(&display);

    pinMode(LED_PIN, OUTPUT);
    //digitalWrite(LED_PIN, HIGH);

    display.print("LoRa node starting.");

    bool paired = usb_mode->start(); // for pairing
    if ( paired ) {
        display.print("LoRa node paired successfully.");
        display.print("This device can now be unplugged.");
        while (true) {
            delay(1000);
        }
        // paired successfully
    }

    display.print("Node will start in 10 seconds.");
    delay(10000);
    display.end();

    //digitalWrite(LED_PIN, LOW);
}

void loop() {
    uint16_t time_to_sleep = 5; // 65535 max

    // randomise time to sleep

    delay(10 * 1000);

    // will need to be rewritten, turns out it restarts the entire program
    //esp_sleep_enable_timer_wakeup((uint64_t)time_to_sleep * 1000000); // use uint64_t to ensure no overflow
    //esp_deep_sleep_start();


    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);

    //SPI.end(); // for sleep
}