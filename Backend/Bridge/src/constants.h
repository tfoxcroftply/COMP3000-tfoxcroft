#define USB_BAUD 115200
#define USB_BUFFER_SIZE 36
#define USB_IDENTIFIER "tnn:" // passes node commands directly so use tnn instead of tnb
#define USB_CONNECT_COMMAND "tnh:ping:" // don't include \n

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