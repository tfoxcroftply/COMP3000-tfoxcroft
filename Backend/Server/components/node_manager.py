# parent

# handles node_pair and node_receiver

from time import sleep
from dataclasses import dataclass, field
import serial, threading

from components.print import vprint
from components.types import ReturnData

from components.node_receiver import NodeReceiver
from components.node_pair import NodePair

class Node: # move to types file later
    hwid: str # if no other attributes added later, perhaps remove object entirely

class NodeManager:
    def __init__(self, container) -> None:
        self.container = container
        self._connected = False
        self.node_reciever = NodeReceiver(container)
        self.node_pair = NodePair(container)

    async def start(self) -> bool:
        return await self.node_reciever.start()
        
    async def get_node_list(self) -> ReturnData:
        return await self.container.database.read_all("SELECT hwid, name, is_active FROM nodes", None)
    
    async def get_node_info(self, node_hwid: str) -> ReturnData:
        if node_hwid == "":
            return ReturnData()
        
        return await self.container.database.read_one("SELECT * FROM nodes WHERE hwid = ?", (node_hwid,)) # renamed from a debug name
    
