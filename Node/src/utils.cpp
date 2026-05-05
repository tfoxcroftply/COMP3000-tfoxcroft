#include "utils.h"

#include "constants.h"

#include <Arduino.h>

const char* Utils::get_mac_address() {
    static char mac[13]; // 12 bytes (ignoring null). static variable should reset after deep sleep.
    uint64_t mac_bytes = ESP.getEfuseMac(); // get mac
    sprintf(mac, "%012llX", mac_bytes); // useful doc https://www.ibm.com/docs/en/zos/3.1.0?topic=programs-sprintf-format-write-data

    return mac;
}

const char* Utils::generate_transmit_string(float temp, float hum) {
    static char generated[sizeof(SAMPLE_PAYLOAD)]; // easier to use sample payload to get buffer size. should also reset after deep sleep.

    const int16_t new_temp = temp * 10; // constrain to range later
    const int16_t new_hum = hum * 10;

    const char* mac_address = get_mac_address();
    
    if (mac_address == nullptr) { return nullptr; };

    snprintf(generated,
        sizeof(generated),
        "%.3s:%.12s:t%04dh%03db30\n", // battery is temporary, need to find a better recording solution
        IDENTIFIER,
        mac_address,
        new_temp,
        new_hum
    );

    if (strlen(generated) != 30) { return nullptr; } // force exact length

    return generated;
}
