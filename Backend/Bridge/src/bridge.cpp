#include "bridge.h"
#include "constants.h"
#include "read_buffer.h"

#include <Arduino.h>

void Bridge::setup() {
    Serial.begin(USB_BAUD);

    ReadBuffer read_buffer = ReadBuffer(USB_BUFFER_SIZE);

    while (true) {
        while (Serial.available() > 0) {
            char input_byte = Serial.read();
            
            read_buffer.append(input_byte);

            if (input_byte == '\n') {

                if (memcmp(read_buffer.read(), USB_CONNECT_COMMAND, strlen(USB_CONNECT_COMMAND)) == 0) {
                    Serial.write("tnn:connect:\n");
                    connected = true;
                    return;
                }
            }
        }

        delay(1000);
    }
}

// not tested yet
bool Bridge::send(const uint8_t* data_buffer, const size_t buffer_size) { // use buffer size provided by getPacketLength() instead of full buffer
    if (!connected) { return false; }

    // check for valid identifier and buffer size
    uint8_t identifier_length = strlen(USB_IDENTIFIER);
    if (identifier_length > buffer_size || buffer_size != USB_BUFFER_SIZE - 1) { return false; } // deny buffer sizes that are too small

    const bool prefix_check = memcmp(data_buffer, USB_IDENTIFIER, identifier_length) == 0; // check if prefix is valid

    // check for two splitters
    size_t splitter_count = 0; // check if buffer contains two command splitters
    for (size_t i = 0; i < buffer_size; i++) {
        if (data_buffer[i] == ':') {
            splitter_count++;
        }
    }
    const bool splitter_check = splitter_count == 2;

    // comparing check results
    if (!prefix_check || !splitter_check) { return false; }

    // write command
    Serial.write(data_buffer, buffer_size);
    Serial.write("\n");

    return true;
}

void Bridge::ping() { // later only ping upon request
    Serial.write("tnn:ping:\n");
}