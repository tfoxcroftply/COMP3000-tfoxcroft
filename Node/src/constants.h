#pragma once

#define SERIAL_RATE 115200
#define SERIAL_BUFFER_SIZE 32
#define SERIAL_COMMAND_MAX_SIZE 32
#define PAIR_TIME 10 // seconds

#define LED_PIN 25
#define DHT_PIN 4

#define USB_TARGET_IDENTIFIER "tnh"
#define USB_MODE_TICK_SPEED 100

#define SCAN_FREQ 2 // minutes

#define DISPLAY_X 128
#define DISPLAY_Y 64

#define OLED_SCL 15
#define OLED_SDA 4
#define OLED_RST 16
#define OLED_LINE_LENGTH 21

#define LORA_MISO 19
#define LORA_CS 18
#define LORA_SCK 5
#define LORA_IRQ 26
#define LORA_MOSI 27
#define LORA_RST 14

#define LORA_POWER 2
#define LORA_SF 9 // test this later
#define LORA_PAYLOAD_LENGTH 32 // should be enough