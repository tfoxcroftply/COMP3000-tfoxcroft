# serial class (second version) for bridge and lora node pairing
# modules invoke receiveCommand(identifier) and get NodeSerialData type
# DynamicSerial was implemented to allow for software gpio without rewriting the file

from serial import Serial, SerialException
import pigpio

from time import sleep

from components.print import vprint
from components.types import NodeSerialData
from components.host_utils import is_host

class DynamicSerial:
    def __init__(self, baudrate: int, port: str | tuple[str,str] | tuple[int,int], timeout: float, use_software_serial: bool = False):
        self.is_software = use_software_serial

        if not self.is_software:
            self.serial = Serial(baudrate = baudrate)
            self.serial.timeout = timeout
            
            if type(port) == tuple:
                self.serial.port = port[0] if is_host() else port[1]
                return
            self.serial.port = port

        else:
            if not type(port) == tuple:
                vprint("Unable to configure software serial. GPIO not defined.", error=True)
                return
            
            self.pi = pigpio.pi()
            if not self.pi.connected:
                vprint("Unable to configure software serial. Could not find pigpio daemon.")
                return
            
            self.pins = port
            self.baud = baudrate
            self.pi.set_mode(port[0], pigpio.OUTPUT)
            self.pi.set_mode(port[1], pigpio.INPUT)

            try: # clean any old processes
                self.pi.bb_serial_read_close(port[1])
            except:
                pass

    def open(self) -> None:
        if not self.is_software:
            self.serial.open()
        else:
            self.pi.bb_serial_read_open(self.pins[1], self.baud)

    def close(self) -> None:
        if not self.is_software:
            self.serial.close()
        else:
            self.pi.bb_serial_read_close(self.pins[1])

    def clear(self) -> None:
        if self.is_software:
            self.serial.reset_input_buffer()
        else:
            while True:
                count, data = self.pi.bb_serial_read(self.pins[1])
                if count <= 0:
                    break

    def readline(self) -> bytes:
        if not self.is_software:
            return self.serial.readline()
        else:
            try:
                count, data = self.pi.bb_serial_read(self.pins[1])
                if count > 0:
                    print(data)
                    return data
                
            except Exception as e:
                vprint(f"Error when reading incoming software serial data. {e}")

    def write(self, data: bytes) -> int | None:
        if not self.is_software:
            return self.serial.write(data)
        else:
            self.pi.wave_clear()
            self.pi.wave_add_serial(self.pins[0], self.baud, data)
            wave = self.pi.wave_create()
            self.pi.wave_send_once(wave)

            #print(wave)

            while self.pi.wave_tx_busy(): # perhaps use a timeout later
                pass
        
    def is_open(self) -> bool:
        if self.is_software:
            return self.pi.connected
        else:
            return self.serial.is_open
        

class NodeSerial:
    def __init__(self, container, baudrate: int, port: str | tuple[str,str], timeout: int = 1, use_software_serial: bool = False):
        self.container = container
        self.serial = DynamicSerial(baudrate, port, timeout, use_software_serial) # maybe separate
        vprint(f"Configured {"software " if use_software_serial else ""}serial port.")
        self._started = False

    def start(self, target_identifier: str):
        self.target_identifier = target_identifier
        self._started = True

    def is_active(self) -> bool:
        return self.serial.is_open()

    def _check_active(self) -> bool:
        if not self._started:
            vprint("Cannot receive serial commands. Module has not been started.")
            return False
        
        if not self.serial.is_open():
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
        try:
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
    
    def _receive_command_logic(self, line: bytes) -> NodeSerialData:
        if len(line) == 0:
            return None # no data found
        
        try:
            decoded_line = line.decode().strip()
        except UnicodeDecodeError as e:
            vprint(f"Error when decoding incoming serial data. {e}")
            return None
        
        except Exception as e:
            vprint("Unknown error when decoding incoming serial data. {e}")
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
                
                found_data: NodeSerialData | None = self._receive_command_logic(line)

                if found_data is not None:
                    return found_data

        except SerialException as e:
            vprint(f"Serial error when reading incoming serial data. {e}")
            self._handle_serial_error()

        except Exception as e:
            vprint(f"Unknown error when reading incoming serial data. {e}")

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
            vprint(f"Error when writing to serial. {e}")
        return False

    # connection handling

    def connect(self, force: bool = False) -> bool:
        if self.serial.is_open() and not self.serial.is_software: # probably will be checked in start() anyway
            if not force:
                vprint("Unable to open serial port. Serial port is already connected.")
                return False
            
            self.serial.close()

        #if self.serial.port is None: # port is required so probably redundant
         #   vprint("Unable open serial. No port has been defined.")
        
        try:
            self.serial.open()
            return True # if this runs it probably worked
        
        except SerialException as e:
            vprint(f"Unable to open serial port. {e}")

        return False


    def _disconnect(self) -> bool:
        raise NotImplementedError
