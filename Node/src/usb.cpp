// replace read buffer with read buffer module from bridge later

#include "usb.h"

#include <Arduino.h>
#include <cstring>

#include "constants.h"

bool led_state = false;

void USB_Mode::handle_command(const char* input_buffer) {
    led_state = !led_state; // for debug
    digitalWrite(LED_PIN, led_state);
    return;
}

void USB_Mode::setup(uint8_t timeout) {
    if (started) { return; };

    Serial.begin(115200);
    Serial.setTimeout(timeout);

    unsigned long time = millis();
    bool has_run = false;

    while (millis() - time < timeout * 1000UL) {
        while (Serial.available() > 0) {
            read_buffer.update(Serial.read());
            Serial.println(read_buffer.read());
            if (read_buffer.has("tnh:connect") == true) {
                digitalWrite(LED_PIN, HIGH);
                Serial.println("tnn:connect");
                connected = true;
                main();
                return;
            }
        }
        delay(1000);
    }

    digitalWrite(LED_PIN, LOW);
    Serial.end();
    return;
}

bool USB_Mode::is_connected() {
    return connected;
}

void USB_Mode::main() {
    read_buffer.clear();
    while (connected) { // change this maybe
        while (Serial.available() > 0) {
            char data = Serial.read();
            if (data == '\n') { // line break
                handle_command(read_buffer.read());
                read_buffer.clear();
            }
        }
        delay(USB_MODE_TICK_SPEED);
    }
    return;
}

USB_Mode::Read_Buffer::Read_Buffer() {
    clear();
}

void USB_Mode::Read_Buffer::update(char input_byte) {
    if (input_byte == '\0' or input_byte == '\r' or input_byte == '\n') { return; };

    if (read_buffer_index >= SERIAL_BUFFER_SIZE - 1) {
        memmove(read_buffer, read_buffer + 1, SERIAL_BUFFER_SIZE - 1);
        read_buffer_index--;
    }

    read_buffer[read_buffer_index++] = input_byte;
    read_buffer[read_buffer_index] = '\0';
}

const char* USB_Mode::Read_Buffer::read() {
    return read_buffer; 
}

bool USB_Mode::Read_Buffer::has(const char* input_buffer) {
    return std::strstr(read_buffer, input_buffer) != nullptr;
}

void USB_Mode::Read_Buffer::clear() {
    read_buffer_index = 0;
    read_buffer[0] = '\0';
}


