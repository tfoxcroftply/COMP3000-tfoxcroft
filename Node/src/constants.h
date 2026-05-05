#pragma once

// node settings
#define FREQ_MIN 180 // seconds
#define FREQ_MAX 300

#define CREATE_DEBUG_READINGS false // debug readings instead of dht
#define DEBUG_READINGS_MIN 20 // temp only
#define DEBUG_READINGS_MAX 30

// others
#define IDENTIFIER "tnn"
#define SAMPLE_PAYLOAD "tnn:000000000000:t0000h000b00\n"

// serial settings
#define SERIAL_RATE 115200
#define SERIAL_BUFFER_SIZE 32
#define SERIAL_COMMAND_MAX_SIZE 32
#define SERIAL_DETECT_TIME 5 // seconds
#define SERIAL_TARGET_IDENTIFIER "tnh"
#define SERIAL_MODE_TICK_SPEED 100

// pins
#define LED_PIN 25
#define DHT_PIN 22

// display settings
#define DISPLAY_X 128
#define DISPLAY_Y 64

// display pins
#define OLED_SCL 15
#define OLED_SDA 4
#define OLED_RST 16
#define OLED_LINE_LENGTH 21

// lora settings
#define LORA_POWER 14
#define LORA_PAYLOAD_SIZE 31 // not including preabmle
#define LORA_SF 9 // spreading factor
#define LORA_BW (float)125.0 // bandwidth in khz
#define LORA_PA 8 // preamble length, default 8
#define LORA_CR 6 // code rate, 4/?

// lora pins
#define LORA_MISO 19
#define LORA_CS 18
#define LORA_SCK 5
#define LORA_IRQ 26
#define LORA_MOSI 27
#define LORA_RST 14

/* packet size 30 (31 including null terminator but unsure if it gets transmitted, check later) 
spreading factor 9
bandwidth 125khz
coding rate 4/5
preamble size 8 */