#pragma once

class USB_Mode {
    public:
        bool setup();
        bool is_enabled();
    private:
        bool usb_mode = false;
};
