#include <Arduino.h>
#include <Preferences.h>
#include <DHT.h>

#include "constants.h"
#include "usb.h"

#define DHT_TYPE DHT22

unsigned int tick_delay = 10000;
Preferences dataStorage;
USB_Mode usb_mode;
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
    pinMode(LED_PIN, OUTPUT);

    dht.begin();
    dataStorage.begin("test", false);

    unsigned int value = dataStorage.getUInt("testValue", 0);
    Serial.println("Session: " + String(value) + ".");
    dataStorage.putUInt("testValue", ++value);

    usb_mode.setup();

    Serial.begin(SERIAL_RATE);
}

void loop() {
    Serial.println("Test");
    delay(2000);
}