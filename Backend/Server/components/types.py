# config and types

from dataclasses import dataclass, field
from typing import Any, Sequence, Literal
from enum import Enum, auto

@dataclass(slots=True)
class _Config: # temporary config location, might make a dedicated file for it
    usb_port: str = "COM5" # let host_info handle in future for environment changes
    usb_baud: int = 115200 # for both esp and sms
    usb_max_time: int = 60 # seconds
    usb_timeout: int = 3 # seconds to wait after last command as to not disrupt ongoing data transmission
    usb_timeout_connect: int = 10 # seconds to allow for connection attempts

    bridge_port: str = "COM6"
    bridge_baud: int = 115200
    bridge_disable_retries_in_debug: bool = True # speeds up startup if bridge is not present
    bridge_refresh_speed: int = 5 # duration between checks for incoming serial commands in seconds
    bridge_start_retries: int = 10 # times to retry bridge connection upon module start. allows the bridge start up fully

    sms_port: str | None = None # can be disabled for dev environment
    sms_baud: int = -1 # temporary until the correct baud is found
    #sms_max_messages_per_timeframe
    #sms_message_timeframe_length

    web_port: int = 80
    websocket_port: int = 8080
    websocket_timeout: int = 10 # websocket inactivity timeout
    serial_debug: bool = False # for node manager stuff

    lora_scan_frequency: int = 1 # every x minutes check for lora data in bridge buffer

    debug: bool = False # gets overriden if running in dev environment
    debug_node_count: int = 0 # amount of nodes to create with database with debug mode active
    debug_create_readings: bool = False # creates some sample values in dev mode
    debug_serial: bool = True # option to mute serial vprints, lots of messages are generated

    print_module_spacing: int = 15 # width of the module identifier when printing

    clear_database: bool = True # wipe database on start, might make dependant on environment
    max_notifications_to_send: int = 10

@dataclass
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
    temperature: int | None
    humidity: int | None
    node_hwid: int | None # keep last, sometimes omitted

class DataTypeEnum:
    ALL = auto()
    TEMPERATURE = auto()
    HUMIDITY = auto()