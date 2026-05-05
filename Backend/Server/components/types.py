# config and types file

from dataclasses import dataclass, field
from typing import Any, Sequence, Literal
from enum import Enum, auto

@dataclass(slots=True)
class _Config: # temporary config location, might make a dedicated file for it
    usb_port: tuple[str,str] = ("/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0", "COM5") # (normal, dev)
    usb_baud: int = 115200 # for both esp and sms
    usb_max_time: int = 60 # seconds
    usb_timeout: int = 3 # seconds to wait after last command as to not disrupt ongoing data transmission
    usb_timeout_connect: int = 10 # seconds to allow for connection attempts

    bridge_port: str = "COM3"
    bridge_gpio: tuple[int, int] = (23, 24) # (output, input)
    bridge_baud: int = 9600 # keep slower for software serial
    bridge_disable_retries_in_debug: bool = True # speeds up startup if bridge is not present
    bridge_refresh_speed: int = 5 # duration between checks for incoming serial commands in seconds
    bridge_start_retries: int = 5 # times to retry bridge connection upon module start. allows the bridge start up fully

    sms_port: str = "/dev/serial0" # for production environment only
    sms_baud: int = 115200 # temporary until the correct baud is found

    web_port: int = 80
    websocket_port: int = 8080
    websocket_timeout: int = 10 # websocket inactivity timeout
    serial_debug: bool = False # for node manager stuff

    lora_scan_frequency: int = 5 # every x minutes check for lora data in bridge buffer
    node_inactivity_time: int = 10 # minutes since last activity until nodes are counted as offline
    threshold_cooldown: int = 0 # minimum time in mins between threshold notifications

    debug: bool = False # gets overriden if running in dev environment
    debug_node_count: int = 0 # amount of nodes to create with database with debug mode active
    debug_create_reading: bool = False # creates some sample values in dev mode
    debug_serial: bool = False # option to mute serial vprints, lots of messages are generated

    print_module_spacing: int = 15 # width of the module identifier when printing
    clear_database: bool = False # wipe database on start, might make dependant on environment
    max_notifications_to_send: int = 10 # limit of notifications to load at one time

class Container:
    config = _Config()

class DatabaseTask(Enum):
    READ_ONE = auto()
    READ_ALL = auto()
    WRITE = auto()

class PrintType(Enum):
    GENERAL = "0" # keep as string
    ERROR = "31"
    
@dataclass(frozen=True, slots=True)
class ReturnData:
    data: Any | None = None
    success: bool = False

@dataclass(frozen=True, slots=True)
class NodeSerialData:
    identifier: str
    command: str
    data: str | None

class NotificationType(Enum):
    GENERAL = auto()
    WARN = auto()
    ERROR = auto()

@dataclass(slots=True)
class DataBlock:
    timestamp: int
    temp: float | None
    hum: float | None
    node_hwid: str # keep last, sometimes omitted. also changed to string.

@dataclass(slots=True)
class ThresholdData:
    id: int | None = None
    name: str | None = None
    threshold_type: str | None = None
    value: int | None = None
    triggered: int | None = None
    last_trigger: int | None = None
    enabled: int | None = None

class DataTypeEnum:
    ALL = auto()
    TEMPERATURE = auto()
    HUMIDITY = auto()