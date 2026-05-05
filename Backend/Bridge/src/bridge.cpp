#include "bridge.h"

#include "constants.h"
#include "read_buffer.h"

#include <Arduino.h>

Bridge::Bridge(uint16_t read_buffer_size) : read_buffer(read_buffer_size) {}
HardwareSerial uart(2);

void Bridge::setup() {
    Serial.begin(115200);
    uart.begin(USB_BAUD, SERIAL_8N1, UART_RX, UART_TX);

    while (true) {
        while (uart.available() > 0) {
            int input_byte = uart.read();
            Serial.write(input_byte);
            read_buffer.append(input_byte);

            if (input_byte == '\n') {
                if (strcmp(read_buffer.read(), USB_CONNECT_COMMAND) == 0) { // changed to strcmp. ADD SIZE CHECK
                    uart.write("tnn:connect:\n");
                    connected = true;
                    return;
                }
            }
        }
        delay(1000);
    }
}

bool Bridge::send(const char* data_buffer, const size_t buffer_size) { // use buffer size provided by getPacketLength() instead of full buffer
    if (!connected) { return false; }

    // check for valid identifier and buffer size
    //uint8_t identifier_length = strlen(USB_IDENTIFIER);
    //if (identifier_length > buffer_size || buffer_size != USB_BUFFER_SIZE - 1) { return false; } // deny buffer sizes that are too small

    if (buffer_size != sizeof(SAMPLE_PAYLOAD)) { return false; } // buffer size probably doesnt include null terminator in the count, check later

    const bool prefix_check = memcmp(data_buffer, USB_IDENTIFIER, strlen(USB_IDENTIFIER)) == 0; // check if prefix is valid

    // check for two splitters
    size_t splitter_count = 0; // check if buffer contains two command splitters
    for (size_t i = 0; i < buffer_size; i++) {
        if (data_buffer[i] == ':') {
            splitter_count++;
        }
    }

    // comparing check results
    if (!prefix_check || splitter_count != 2) { return false; }

    // write command
    uart.write(data_buffer, buffer_size);

    return true;
}

void Bridge::ping() { // later only ping upon request
    uart.write("tnn:ping:\n");
}