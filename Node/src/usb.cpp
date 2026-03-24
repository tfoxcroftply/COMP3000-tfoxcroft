#include "usb.h"

#include "constants.h"
#include "read_buffer.h"

#include <Arduino.h>
#include <cstring>

USBMode::USBMode(DisplayClass* input_display) : read_buffer(SERIAL_BUFFER_SIZE) {
    display = input_display;
};

void USBMode::send_pair_command() {
    // could reuse read_buffer.cpp later
    // format "tnn:111111111111:pair"

    char pair_command[23]; // 4 + 5 + 12 + 1 = 22
    char mac[13]; // 12 bytes (ignoring null)

    char identifier[] = "tnn:"; // 4 bytes (ignoring null)
    char command[] = ":pair"; // 5 bytes (ignoring null)

    uint64_t mac_bytes = ESP.getEfuseMac(); // get mac
    sprintf(mac, "%012llX", mac_bytes); // useful doc https://www.ibm.com/docs/en/zos/3.1.0?topic=programs-sprintf-format-write-data
    //mac[12] = '\0'; snprintf should handle null terminator

    strcpy(pair_command, identifier); // add identifier
    strcat(pair_command, mac); // add mac
    strcat(pair_command, command); // add command
    strcat(pair_command, "\n"); // newline

    Serial.write(pair_command); // send pair command

    // verify if it has been recieved

    return;
}

bool USBMode::start() {
    if (running) { return false; };

    read_buffer = ReadBuffer(SERIAL_BUFFER_SIZE);

    Serial.begin(115200); // start serial
    Serial.setDebugOutput(false);

    uint32_t time = millis(); // returns unsigned long but uint32_t should be the same

    while (millis() - time < PAIR_TIME * 1000) {
        while (Serial.available() > 0) {
            if (!hasRun) {
                display->print("USB detected. Ensure hub is in pairing mode.");
                hasRun = true;
            }

            int byte = Serial.read();
            read_buffer.append(byte);

            if (byte == '\n') {
                paired = handle_command();
                read_buffer.clear();
                if (paired == true) {
                    return true;
                }
            }
        }
        delay(1000);
    }

    return false;
}

bool USBMode::handle_command() {
    //display->clear();

    //char read_buffer_copy[SERIAL_BUFFER_SIZE + 1]; // make copy
    //memcpy(read_buffer_copy, read_buffer.read(), sizeof(read_buffer_copy)); // copy useful part, change to strcpy if reused
    //display->print(read_buffer_copy);

    // tnh:connect:
    if (read_buffer.has("tnh:paired:\n")) { 
        return true;
     }

    if (read_buffer.has("tnh:connect:\n")) { 
        digitalWrite(LED_PIN, HIGH);
        send_pair_command();
    }

    return false; 

    // old code from a modular command handler
    //size_t index = strcspn(read_buffer.read(), "tnh:"); // get index
    //char read_buffer_copy[SERIAL_BUFFER_SIZE + 1]; // make copy
    //memcpy(read_buffer_copy, read_buffer_copy + index, sizeof(read_buffer_copy) - 1); // copy useful part   
}