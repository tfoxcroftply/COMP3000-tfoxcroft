from time import sleep
import serial, threading

from components.print import vPrint

class NodeManager:
    _connected = False # use later

    def __init__(self, container) -> None:
        self.container = container

    def start(self, baud_rate: int = 115200) -> None:
        self.serial = serial.Serial(baudrate=baud_rate) # dont include port here
        self.serial.port = "COM4" # change port depending on host later
        threading.Thread(target=self._detect_loop,daemon=True).start()

    def request_node_connection(self) -> bool: # unused as of now
        return self._connected
    
    def debug(self) -> None:
        if self.serial.is_open:
            self.serial.write(b"tnh:testcommand\n")

    def _disconnect(self, error: str = "Unknown error") -> None:
        if self.serial.is_open:
            self.serial.close()
        if self.container.config.serial_debug:
            vPrint(f"Node connection error: {error}.")
    
    def _connected_loop(self) -> None:
        sleep(1)

    def _detect_loop(self) -> None:
        def request_connect() -> None:
            try:
                if self.serial.is_open:
                    self._disconnect()
                self.serial.open()
                if self.serial.is_open:
                    self.serial.write(b"tnh:connect\n")
                    if self.container.config.serial_debug:
                        vPrint("> tnh:connect")
            except serial.SerialException as e:
                if self.container.config.serial_debug:
                    vPrint(f"Node connection error: {e}.")

        def read_input() -> bool:
            try:
                lines = self.serial.read_all() # temporary debug logic
                if self.container.config.serial_debug:
                    print(lines)
                for line in lines.splitlines():
                    try:
                        line = line.decode()
                        if line == "tnn:connect":
                            vPrint("< " + line)
                            return True
                    except UnicodeDecodeError:
                        vPrint("Serial input decode error.")

            except serial.SerialException:
                self._disconnect()

            return False
            
        while True: # change later
            if not self.serial.is_open:
                request_connect()
            else:
                if read_input():
                    vPrint("Node connected successfully.")
                    self._connected_loop()

            #vPrint("Node manager module tick.")
            sleep(2)

