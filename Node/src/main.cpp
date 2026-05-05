// rewrite

#include "constants.h"

#include "display_class.h"
#include "usb.h"
#include "utils.h"

#include <Arduino.h>
#include <Preferences.h>
#include <DHT.h>
#include <RadioLib.h>

#define DHT_TYPE DHT22

SX1276 radio = new Module(LORA_CS, LORA_IRQ, LORA_RST, -1);
DisplayClass display;
USBMode usb_mode;
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
    // initialise devices
    dht.begin();
    pinMode(LED_PIN, OUTPUT);

    //delay(1000); for lora to start up properly - unused because usb_mode provides enough delay

    // detect usb mode and enter pairing
    if (usb_mode.start()) {
        display.setup(); // only set up in usb mode
        display.print("Successfully sent node pairing information.");

        while (true) {
            for (uint8_t i = 0; i < 3; i++) {
                digitalWrite(LED_PIN, HIGH);
                delay(200);
                digitalWrite(LED_PIN, LOW);
                delay(200);

                if (i == 2) {
                    delay(2000);
                }
            }
        }
    }

    // data collection
    float temp, hum;

    if (CREATE_DEBUG_READINGS) {
        temp = DEBUG_READINGS_MIN + ((float)esp_random()) / float(UINT32_MAX) * ((float)DEBUG_READINGS_MAX - (float)DEBUG_READINGS_MIN);
        hum = 50.0;
    } else {
        temp = dht.readTemperature();
        hum = dht.readHumidity();
    }

    if (isnan(temp) || isnan(hum)) { // flash led if error
        for (uint8_t i = 0; i < 3; i++) {
            digitalWrite(LED_PIN, HIGH);
            delay(100);
            digitalWrite(LED_PIN, LOW);
            delay(100);
        }
    } else {
        // transmission
        digitalWrite(LED_PIN, HIGH);
        delay(50);
        digitalWrite(LED_PIN, LOW);

        SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);
        const bool state = radio.begin(868.0, LORA_BW, LORA_SF, LORA_CR);

        if (state == RADIOLIB_ERR_NONE) {
            radio.setOutputPower(LORA_POWER);
            const char* generated_payload = Utils::generate_transmit_string(temp, hum);
            if (generated_payload != nullptr) {
                radio.transmit(generated_payload); // blocking, no delay needed
                //delay(LORA_TRANSMIT_DURATION);
            }
         }
         radio.sleep();
    }

    uint16_t sleep_duration = FREQ_MIN + ((float)esp_random()) / float(UINT32_MAX) * ((float)FREQ_MAX - (float)FREQ_MIN);

    esp_sleep_enable_timer_wakeup((uint64_t)sleep_duration * 1000000);
    esp_deep_sleep_start();
}

void loop() {} // needs to be defined but shouldn't run