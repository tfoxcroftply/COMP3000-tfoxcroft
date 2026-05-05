# https://cdn-shop.adafruit.com/datasheets/sim800_series_at_command_manual_v1.01.pdf

# responsible for managing the sms module and other related functions

from serial import Serial, SerialException
from time import time
from re import search, compile

from components.print import vprint
from components.types import ReturnData
from components.host_utils import is_host

class GSMModem:
    def __init__(self, container, port: str, baud: int = 115200, timeout: float = 3):
        self.container = container
        if is_host():
            self.serial = Serial(port, baud, timeout=timeout)
        self.started = False

    def send_command(self, command: str, timeout: float = 3, expect_response: bool = False, expect_string: str | None = None) -> str | None:
        self.serial.reset_input_buffer()
        self.serial.write((command + "\r").encode("ascii", errors="ignore"))
        self.serial.flush()

        end = time() + timeout
        response = b""

        while time() < end:
            response += self.serial.read()
            decoded = response.decode("ascii", errors="ignore").strip()

            if expect_response and expect_string is not None:
                if expect_string in decoded:
                    return "OK"

            if "OK" in decoded:
                if expect_response:
                    return decoded.replace("OK","").strip() # removes blank lines
                return "OK"
            
        vprint(f"Timeout when waiting for SMS module command. Sent \"{command}\"." + f" Waited for \"{expect_string}\"" if expect_string else "", error=True)

    def receive_data(self, command) -> str | None:
        return self.send_command(command, expect_response=True)
    
    def send_message(self, recipient: str, message: str) -> bool:
        if not self.is_active(): return False

        sent: str | None = self.send_command(f"AT+CMGS=\"{recipient}\"", expect_response=True, expect_string=">")
        if sent is None:
            return False
        return self.send_command(f"{message}\x1A", expect_response=True, expect_string="+CMGS:") == "OK"
    
    def is_active(self) -> bool:
        if not self.started: return False
        response = self.send_command("AT") == "OK"
        return response

    def start(self):
        if self.started or not is_host(): return
        self.started = True

        self.send_command("AT") # test
        self.send_command("ATE0") # echo off
        self.send_command("AT+CMGF=1") # text mode

        vprint("SMS module started successfully.")

class SMS:
    def __init__(self, container):
        self.container = container
        self.modem = GSMModem(self.container, self.container.config.sms_port, self.container.config.usb_baud)
        self._started = False

    async def get_recipient(self) -> ReturnData:
        found: ReturnData = await self.container.database.read_one("SELECT * FROM settings WHERE key = 'sms_recipient'")
        if not found.success:
            temp = "Unable to retrieve phone number."
            vprint(temp)
            return ReturnData(temp)
        if found.data is None:
            temp = "No phone number was found."
            vprint(temp)
            return ReturnData(None, True)
        
        return ReturnData(found.data["value"], True)

    async def _check_status(self) -> bool:
        if not self._started or not self.modem.is_active():
            vprint("SMS module has not been started and/or module is disconnected.", error=True)
            return False
        
        found: ReturnData = await self.get_recipient()
        if not found.success or found is None:
            return False

        return True

    async def start(self) -> bool:
        if not is_host():
            vprint("SMS module cannot start. Unable to run in development environment.", error=True)
            return False

        if self.container.config.sms_port == None:
            vprint("SMS module cannot start. Config has no port defined.", error=True)
            return False
        
        try:
            self.modem.start() # maybe use pin later
            self._started = True

            #await self.send_message("Testing message")
        except Exception as e:
            #import traceback
            #traceback.print_exc()
            vprint(f"Failed to start SMS module: '{e}'", error=True)

        return False
    
    async def is_enabled(self) -> ReturnData:
        return ReturnData(success=True)

        write: ReturnData = await self.container.database.write("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", ("sms_enabled",1))
        if not write.success:
            return ReturnData("Failed to find settings data.")
        
        found: ReturnData = await self.container.database.read_one("SELECT * FROM settings where KEY = 'sms_enabled'")
        if not found.success:
            return ReturnData("Failed to check whether SMS is enabled.")
        
        return ReturnData(found.data, True)

    async def set_recipient(self, number_string: str) -> ReturnData:
        #if not self._check_status(): return ReturnData()

        number_string = number_string.strip()

        #^\+44\d{10}$
        pattern = compile("^\\+447\\d{9}$")
        if not bool(pattern.match(number_string)):
            return ReturnData("Invalid phone number supplied. Phone number must be start with +44 followed by 10 digits.")

        found: ReturnData = await self.get_recipient()
        if not found.success:
            return ReturnData("Error when comparing existing recipient phone number.")
        
        if found.data == number_string:
            return ReturnData("Provided phone number is already set.")

        if not len(str(number_string)) > 10:
            return ReturnData("Provided phone number is too short.")
        
        write: ReturnData = await self.container.database.write("INSERT INTO settings (key, value) VALUES ('sms_recipient', ?) ON CONFLICT(key) DO UPDATE SET VALUE = excluded.value",(number_string,))
        if write.success:
            vprint("Successfully set SMS recipient.")
            return ReturnData(success=True)
        
        return ReturnData("Database error when setting SMS recipient.")
    
    async def send_message(self, message: str) -> ReturnData:
        if not await self._check_status(): return ReturnData()

        found: ReturnData = await self.get_recipient()
        if not found.success or found.data is None:
            return ReturnData("Error when finding recipient phone number.")

        if self.modem.send_message(found.data, message):
            vprint("SMS command sent to modem.")
            return ReturnData(success=True)
        
        vprint("Failed to send SMS command to modem.")
        return ReturnData()

    async def get_signal(self) -> int:
        if not self.modem.is_active(): return -1
        
        response = self.modem.receive_data("AT+CSQ")

        match = search(r"\+CSQ:\s*(\d+),(\d+)", response)
        if match is None: return -1

        signal = int(match.group(1))

        return signal # -1 and 0-99
    
    async def set_enabled(self, enabled: int) -> ReturnData:
        return await self.container.database.write("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET key = excluded.key, value = excluded.value", ("sms_enabled", enabled,))

