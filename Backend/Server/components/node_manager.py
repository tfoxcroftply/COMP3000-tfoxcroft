# primary node handling module
# responsible for managing all nodes
# handles node_pair and node_receiver

from time import sleep, time
from dataclasses import dataclass, field
from re import compile
import serial, threading

from components.print import vprint
from components.types import ReturnData, DataBlock

from components.node_receiver import NodeReceiver
from components.node_pair import NodePair

class Node: # move to types file later
    hwid: str # if no other attributes added later, perhaps remove object entirely

class NodeManager:
    def __init__(self, container) -> None:
        self.container = container
        self._connected = False
        self.node_receiver = NodeReceiver(container)
        self.node_pair = NodePair(container)

    async def start(self) -> bool:
        return await self.node_receiver.start()
    
    #async def _node_update(self) -> ReturnData: # should be run before most requests
        #currentTime = int(time())
        #write: ReturnData = await self.container.database.write("UPDATE nodes SET is_active = 0 WHERE last_seen <= ?",(currentTime - self.container.config.node_inactivity_time,))
        #if not write.success:
            #vprint("Error when updating node last seen time.")

    async def get_node_list(self) -> ReturnData:
        #await self._node_update()
        return await self.container.database.read_all("SELECT * FROM nodes", None)
    
    async def get_node_info(self, node_hwid: str) -> ReturnData:
        if node_hwid == "":
            return ReturnData()
        
        #await self._node_update()
        return await self.container.database.read_one("SELECT * FROM nodes WHERE hwid = ?", (node_hwid,)) # renamed from a debug name
    
    async def add_node(self, node_hwid: str) -> ReturnData:
        node_hwid = node_hwid.upper()

        #pattern = compile("^\\[0-9A-F]{12}$")
        #if not bool(pattern.match(node_hwid)):
            #return ReturnData("Invalid HWID format.")

        check = await self.get_node_info(node_hwid)
        if check.data is not None and check.success:
            return ReturnData("Node already exists.", success=False)

        count: ReturnData = await self.get_node_list()
        if not count.success: return ReturnData()

        write: ReturnData = await self.container.database.write("INSERT INTO nodes (hwid, name) VALUES (?, ?)", (str(node_hwid), "Node " + str(len(count.data) + 1),))
        if write and write.success:
            return ReturnData(success=True)
        
        return ReturnData()
    
    async def update_node(self, name: str, node_hwid: str, disabled: int):
        found: ReturnData = await self.container.database.read_one("SELECT * FROM nodes WHERE hwid = ?",(node_hwid,))

        if found.success and len(found.data) == 0:
            temp = "Unable to update node information. Node was not found."
            vprint(temp)
            return ReturnData(temp)
        
        write: ReturnData = await self.container.database.write("UPDATE nodes set name = ?, disabled = ? WHERE hwid = ?",(name, disabled, node_hwid))
        if write.success:
            return ReturnData(success=True)
        
        return ReturnData("Unknown error when updating node information.")

        
    async def update_node_information(self, node: DataBlock) -> ReturnData: # for time tracking, not for user updates
        found: ReturnData = await self.container.database.read_one("SELECT * FROM nodes WHERE hwid = ?",(node.node_hwid,))
        if not found.success:
            vprint("Error when searching for existing node.")
            return ReturnData()

        if len(found.data) == 0:
            vprint("Unable to update node information. Node was not found.")
            return ReturnData()
        
        currentTimestamp = int(time())

        write: ReturnData = await self.container.database.write("UPDATE nodes SET last_seen = ? WHERE hwid = ?",(currentTimestamp, node.node_hwid,))
        if not write.success:
            vprint("Error when updating node last seen time.")
            return ReturnData()

        vprint("Successfully updated node last seen time.")
        return ReturnData(success=True)
