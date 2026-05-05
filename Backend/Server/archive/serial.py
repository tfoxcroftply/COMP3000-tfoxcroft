# old version
# half works

# serial module
# gets port info from host_info
# remember to invoke commands elsewhere

# format: identifier:command:data eg. tnh:test:12345

from serial import Serial, SerialException
from time import time
from asyncio import wait_for, sleep, CancelledError
from dataclasses import dataclass

from components.print import vprint
from components.types import ReturnData, NodeSerialData

class NodeSerial:
    def __init__(self, container):
        self.container = container
        self._serial_active: bool = False
        self.message_list: list[str] = []
        self.serial = Serial(baudrate = self.container.config.usb_baud) # maybe separate
        self._started: bool = False

    def start(self, port: str, target_identifier: str):
        self.serial.port = port
        self.serial.timeout = 1
        self.target_identifier = target_identifier
        self._started = True

    def is_serial_active(self) -> bool:
        return self.serial.is_open # maybe change later to internal tracking value
    
    def _append_to_log(self, string: str) -> None: # remove this function
        self.message_list.append(string)

    def send_command(self, input: str) -> bool:
        bytes_sent: int = self.serial.write((input + "\n").encode())
        return bytes_sent > 0

    def parse_command(self, input_data: str) -> NodeSerialData | None: # maybe move to regex
        start = input_data.find(f"{self.target_identifier}:")
        if start == -1:
            vprint("Failed to parse serial command. Identifier is not present.", error=True)
            return None

        end = input_data.find("\n", start)
        if end == -1: 
            vprint("Failed to parse serial command. Newline is not present.", error=True)
            return None
        
        selected = input_data[start:end]
        splitted = selected.split(":", 2)
        if not len(splitted) == 3 or splitted[0] != self.target_identifier:
            vprint("Failed to parse serial command. Command format is not recognised.", error=True)
            return None
        
        command: str = splitted[1]
        data: str = splitted[2]

        return NodeSerialData(command, data)

    async def receive_commmand(self, specific: str | None = None, timeout: int = 1, _starting: bool = False) -> ReturnData:
        if not _starting and not self._serial_active:
            vprint("Unable to receive serial commands. Serial is not active.", error=True)
            return ReturnData()
        
        try:
            for i in range(timeout):
                lines = self.serial.readlines()

                if not lines or len(lines) == 0: continue

                for line in lines:
                    try:
                        decoded = line.decode()
                        decoded = decoded.strip() 
                        if specific is not None and specific not in decoded: # specific was specified and nothing was found
                            continue
                            
                        parsed_command: NodeSerialData | None = self.parse_command(decoded + "\n") # sends without checking, would fail to except block below if invalid
                        if parsed_command is not None:
                            return ReturnData(parsed_command, True)
                        
                    except UnicodeDecodeError:
                        vprint("Error when decoding serial input stream. Continuing.", error=True)
                        continue

                await sleep(1)

        except SerialException as e:
            vprint("Serial error when reading incoming data.", error=True)

        except Exception as e:
            vprint("Unknown error when reading incoming data.", error=True)

        return ReturnData()
    
    async def attempt_connect(self, timeout: int | None = None) -> bool:
        if self._serial_active:
            vprint("Serial connection attempt failed. Serial is already connected.", error=True)
            return False

        started_time = time()

        vprint(f"Attempting to connect to '{self.target_identifier}'.")

        try:
            new_timeout = timeout if timeout is not None else self.container.config.usb_timeout_connect
            while time() - started_time < new_timeout:
                if not self.serial.is_open:
                    try:
                        self.serial.open()
                    except SerialException as e:
                        print(e)
                else:
                    self.send_command("tnh:connect:")
                    found: ReturnData = await self.receive_commmand(f"{self.target_identifier}:connect:", 1, True)
                    if found.success:
                        vprint(f"Connected to '{self.target_identifier}' successfully.")
                        return True
                
                await sleep(1)
                
        except CancelledError:
            vprint("Serial connection request interrupted.")

        vprint(f"Serial connection to '{self.target_identifier}' failed.", error=True)
        return False

    def open_serial(self) -> bool:
        if not self._started:
            vprint("Failed to open serial. Module not initialised.", error=True)
            return False

        if self._serial_active: 
            vprint("Failed to open serial. Serial is already active!", error=True)
            return False
            
        try:
            self.serial.open()
            if self.serial.is_open:
                self._serial_active = True
                vprint(f"Serial opened successfully. Listening for '{self.target_identifier}'.")
                return True
            
        except Exception as e:
            vprint(f"Error opening serial. '{e}'")
            return False
        
        vprint("Unknown error when opening serial.", error=True)
        return False

        
    def close_serial(self) -> bool: # requested by websocket if timeout
        if not self.serial_active:
            vprint("Failed to close serial. Serial is not active.", error=True)
            return
        
        self.serial_active = False
