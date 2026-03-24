# serial class (second version) for bridge and lora node pairing
# modules invoke receiveCommand(identifier) and get NodeSerialData type
# bridge.py and node_reciever.py

from serial import Serial, SerialException

from components.print import vprint
from components.types import NodeSerialData

class NodeSerial:
    def __init__(self, container):
        self.container = container
        self.serial = Serial(baudrate = self.container.config.usb_baud) # maybe separate
        self._started = False

    def start(self, port: str, target_identifier: str, timeout: int = 1):
        self.serial.port = port
        self.serial.timeout = timeout
        self.target_identifier = target_identifier
        self._started = True

    def is_active(self) -> bool:
        return self.serial.is_open

    def _check_active(self) -> bool:
        if not self._started:
            vprint("Cannot receive serial commands. Module has not been started.")
            return False
        
        if not self.serial.is_open:
            vprint("Cannot receive serial commands. Port is not open. Attempting to reconnect.")

            if not self.connect(True):
                vprint("Failed to reconnect to serial.")
                return False
        
        return True
    
    def _handle_serial_error(self, silent: bool = False) -> bool:
        vprint("Serial error detected, reconnecting.")

        if not self.connect(True):
            vprint(f"Serial device '{self.target_identifier}' disconnected.", error=True)
    
    # command handling

    def _parse_command(self, input: str) -> NodeSerialData | None:
        try: # probably temporary
            strings: list[str] = []

            strings = input.split(":")

            if len(strings) != 3:
                vprint("Unknown format of incoming serial command.")
                return None
            
            if len(strings[0]) != 3 or not strings[0].startswith("tn"):
                vprint("Incoming serial command does not match identifier format.")
                return None
            
            return NodeSerialData(strings[0], strings[1], strings[2])
        
        except Exception:
            vprint("Unknown error when parsing serial command.")
        
        return None
    
    def _recieve_command_logic(self, line: bytes) -> NodeSerialData:
        if len(line) == 0:
            return None # no data found
        
        try:
            decoded_line = line.decode().strip()
        except UnicodeDecodeError as e:
            vprint(f"Error when decoding incoming serial data. {e}")
            return None
        
        except Exception:
            vprint("Unknown error when decoding incoming serial data.")
            return None

        
        parsed_data: NodeSerialData | None = self._parse_command(decoded_line)

        if parsed_data is not None:
            if parsed_data.identifier == self.target_identifier:
                return parsed_data

        return None
 
    def receive_command(self) -> NodeSerialData | None:
        if not self._check_active(): return None
        
        try:
            while self._check_active():
                line: bytes = self.serial.readline()
                if not line:
                    vprint("No incoming serial data found.")
                    return None
                
                vprint(f"Received serial: '{line}'")
                
                found_data: NodeSerialData | None = self._recieve_command_logic(line)

                if found_data is not None:
                    return found_data

        except SerialException as e:
            vprint(f"Serial error when reading incoming serial data. {e}")
            self._handle_serial_error()

        except Exception:
            vprint("Unknown error when reading incoming serial data.")

        return None
        
    def send_command(self, command: str) -> bool:
        if not self._check_active(): return False

        try:
            encoded: bytes = command.encode()
            self.serial.write(encoded)
            vprint(f"Successfully sent '{encoded}' to '{self.target_identifier}'")
            return True
        
        except SerialException as e:
            vprint(f"Serial error when writing to serial. {e}")
            self._handle_serial_error()

        except BytesWarning:
            vprint("Error when encoding serial command.")
        except Exception as e:
            vprint("Error when writing to serial.")
        return False

    # connection handling

    def connect(self, force: bool = False) -> bool:
        if self.serial.is_open: # probably will be checked in start() anyway
            if not force:
                vprint("Unable to open serial port. Serial port is already connected.")
                return False
            
            self.serial.close()

        if self.serial.port is None: # port is required so probably redundant
            vprint("Unable open serial. No port has been defined.")
        
        try:
            self.serial.open()
            return True # if this runs it probably worked
        
        except SerialException as e:
            vprint(f"Unable to open serial port. {e}")

        return False


    def _disconnect(self) -> bool:
        raise NotImplementedError
