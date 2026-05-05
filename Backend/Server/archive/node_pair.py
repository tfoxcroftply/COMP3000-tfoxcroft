# old and buggy, dont use

# handles node pairing
# runs from node_manager
# separated because it includes a lot of serial commands

# websocket should handle serial

from serial import Serial, SerialException
from components.print import vprint
from components.types import ReturnData
from websockets.asyncio.server import serve
from time import sleep, time
from typing import Any

class NodePairing:
    def __init__(self, container):
        self.container = container
        self._started: bool = False
        self._webSocketActive: bool = False
        self._serialActive: bool = False
        self.serial: Serial | None = None
        self._pendingCommands: list[Any] = []
        self._lastSerial: float = -1

    def start(self) -> None:
        if not self.started: return
        self.started = True
        
        self.serial = Serial(baudrate=self.container.config.usb_baud) # remember including port will auto open the connection

    def isSerialActive(self) -> bool:
        return self._serialActive
    
    def serialLoop(self) -> bool:
        def handle_command(command: str, arguments: str, full: str) -> Any:
            match command:
                case "connect":
                    pass
                case "ping":
                    pass

        self._serialActive = True

        try:
            while self.serial.is_open: # check this
                if len(self._pendingCommands) > 0:
                    command = self._pendingCommands.pop(1)
                    if not command: continue

                    self.serial.write(bytes(command))
                    vprint(f"Sent command: '{command}'")
                    continue

                lines = Serial.read_all() # should read until timeout
                for line in lines:
                    decoded = line.decode().strip()

                    start = decoded.find(b"tnn:")
                    end = decoded.find("\n")

                    if not (start and end): continue

                    selected = decoded[start:end]
                    splitted = selected.split(":")

                    if not len(splitted) == 3: continue # needs to be identifier:command:data
                    if not splitted[1] == "tnn": continue

                    vprint(f"received command: '{selected}'")
                    self._lastSerial = time()

                    response: str | None = handle_command(splitted[2], splitted[3])
                    if response is not None:
                        self.serial.write("tnh:" + response) # maybe add identifier:command:data checks

                sleep(0.5) # stops the loop from running as fast as possible

        except SerialException as e: # check if this runs first
            vprint(f"Serial error in communication loop. Closing serial connection. '{e}'")
            self.closeSerial()

        except Exception as e:
            vprint(f"Error in serial communication loop. '{e}'")

        self._serialActive = False


    def openSerial(self) -> bool:
        if self._serialActive:
            vprint("Failed to open serial port. Serial is already open.")
            return False
        
        port: str | None = "COM4" # placeholder. use a function from hostInfo.py

        if not port:
            vprint("Failed to open serial port. Unable to retrieve port information.")
            return False
        
        try:
            self.serial.port = port
            self.serial.open()
            if self.serial.is_open:

                vprint(f"Successfully connected to {self.serial.port}.")
                return True

        except Exception as e:
            vprint(f"Failed to open serial port. {e}")

        vprint("Unknown error when opening serial port.")
        return False

    def closeSerial(self) -> bool:
        if not self._serialActive: 
            vprint("Failed to close serial port. Serial connection is not active.")
            return False
        
        try:
            self.serial.close()
            if self.serial.is_open == False:
                vprint("Serial port successfully closed.")
                return True
        except Exception as e:
            vprint(f"Failed to close serial port. {e}")

        return False
    
    def webSocketStatus(self) -> bool:
        return self._socketActive

    def getWebSocket(self) -> str | None:
        url: str = "asdasdasdasdsa"
        vprint(f"Retrieving websocket port: '{url}'")

        return None
    
    def webSocketLoop() -> None:
        try:
            pass
        except Exception as e:
            pass

    async def startWebSocket(self) -> bool:
        if self._socketActive:
            vprint("Failed to open websocket. Websocket is already active.")
            return False
        
        if self._serialActive:
            vprint("Websocket closed. Serial is already active and pending closure.") # should close after inactivity
            return False
        
        self._webSocketActive = True

        # open socket

        self.webSocketLoop()

        # close socket

        self._webSocketActive = False # check if this runs after an error

    def closeWebSocket(self) -> bool:
        pass


