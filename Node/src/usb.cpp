#include "usb.h"

#include "constants.h"
#include "read_buffer.h"
#include "display_class.h"
#include "utils.h"

#include <Arduino.h>
#include <cstring>

USBMode::USBMode() : read_buffer(SERIAL_BUFFER_SIZE) {};

void USBMode::send_pair_command() {
    // format "tnn:111111111111:pair"

    char pair_command[23];
    const char* mac_address = Utils::get_mac_address();

    snprintf(pair_command, 
        sizeof(pair_command),
        "%4s%12s%5s",
        "tnn:", // 4
        mac_address, // 12
        ":pair", // 5
        "\n" // 1 = 22 + \0 = 23
    );

    Serial.write(pair_command); // send pair command
    return;
}

bool USBMode::start() {
    if (running) { return false; };

    Serial.begin(115200); // start serial
    Serial.setDebugOutput(false); // seems to not change much

    uint32_t time = millis(); // returns unsigned long but uint32_t should be the same

    while (millis() - time < SERIAL_DETECT_TIME * 1000) {
        while (Serial.available() > 0) {
            if (!hasRun) {
                //display->print("USB detected. Ensure hub is in pairing mode.");
                hasRun = true;
            }

            int byte = Serial.read();
            read_buffer.append(byte);

            if (byte == '\n') {
                paired = handle_command();
                read_buffer.clear();
                if (paired == true) {
                    Serial.end(); // may trigger esp restart
                    return true;
                }
            }
        }
        delay(1000);
    }

    Serial.end(); // also may restart the esp, check later
    return false;
}

bool USBMode::handle_command() {
    //display->clear();

    // tnh:connect:
    if (read_buffer.has("tnh:paired:\n")) { 
        return true;
     }

    if (read_buffer.has("tnh:connect:\n")) { 
        send_pair_command();
    }

    return false; 

    // old code from a modular command handler - untested
    //size_t index = strcspn(read_buffer.read(), "tnh:"); // get index
    //char read_buffer_copy[SERIAL_BUFFER_SIZE + 1]; // make copy
    //memcpy(read_buffer_copy, read_buffer_copy + index, sizeof(read_buffer_copy) - 1); // copy useful part   
}