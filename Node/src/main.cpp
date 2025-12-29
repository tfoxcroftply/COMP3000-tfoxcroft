#include "Arduino.h"
#include "Preferences.h"
#include "DHT.h"

#include "usb.h"

#define LED_PIN 2
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define SERIAL_RATE 115200

unsigned int tick_delay = 10000; 
bool led_state = false;

Preferences dataStorage;
USB_Mode usb_mode;
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
    pinMode(LED_PIN, OUTPUT);

    if (usb_mode.setup()) {
        Serial.begin(SERIAL_RATE);
        tick_delay = 2000;
    }

    dht.begin();
    dataStorage.begin("test", false);

    unsigned int value = dataStorage.getUInt("testValue", 0);
    Serial.println("Session: " + String(value) + ".");
    dataStorage.putUInt("testValue", ++value);
}

void usb_loop() {
    float temp = dht.readTemperature();
    if (!isnan(temp)) {
        char stringBuffer[24];
        snprintf(stringBuffer,sizeof(stringBuffer), "Temp: %.2f°C", temp);
        Serial.println(stringBuffer);
    } else {
        Serial.println("DHT read failed.");
    }
}

void main_loop() {
    led_state = !led_state;
    digitalWrite(LED_PIN,led_state);
}

void loop() {
    if (usb_mode.is_enabled()) {
        usb_loop();
    } else {
        main_loop();
    }
    delay(tick_delay);
}

