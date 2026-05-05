#define USB_BAUD 9600
#define USB_BUFFER_SIZE 36
#define USB_IDENTIFIER "tnn:" // passes node commands directly so use tnn instead of tnb
#define USB_CONNECT_COMMAND "tnh:ping:\n" // don't include \n
#define SAMPLE_PAYLOAD "tnn:000000000000:t0000h000b00\n"

#define DEBUG_MODE true

#define DISPLAY_X 128
#define DISPLAY_Y 64

#define LED_PIN 25

#define UART_RX 13
#define UART_TX 17

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

// lora settings
#define LORA_POWER 14
#define LORA_PAYLOAD_SIZE 31 // not including preabmle
#define LORA_SF 9 // spreading factor
#define LORA_BW (float)125.0 // bandwidth in khz
#define LORA_PA 8 // preamble length, default 8
#define LORA_CR 6 // code rate, 4/?