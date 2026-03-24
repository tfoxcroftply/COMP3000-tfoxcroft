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
    
    async def add_node(self, node_hwid: str) -> ReturnData:

        # add more checks later
        # must be 12 characters, all uppercase
        # check esp efuse return value, ensure it stays at a fixed length

        check = await self.get_node_info(node_hwid)
        if check.data is not None and check.success:
            return ReturnData("Node already exists.", success=False)

        count: ReturnData = await self.get_node_list()
        if not count.success: return ReturnData()

        write: ReturnData = await self.container.database.write("INSERT INTO nodes (hwid, name) VALUES (?, ?)", (str(node_hwid), "Node " + str(len(count.data) + 1),))
        if write and write.success:
            return ReturnData(success=True)
        
        return ReturnData(success=False)
    
