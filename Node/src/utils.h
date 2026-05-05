#pragma once

#include <Arduino.h>

namespace Utils {
    const char* get_mac_address();
    const char* generate_transmit_string(float temp, float hum);
};