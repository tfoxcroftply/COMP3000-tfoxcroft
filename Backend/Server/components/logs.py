# manages logs and corresponding information

from datetime import datetime
from dataclasses import dataclass, field

from components.print import vprint
from components.types import ReturnData, DataBlock

@dataclass(slots=True)
class Log:
    def __init__(self, container):
        self.container = container
        self._loaded: bool = False
        self.readings: list[DataBlock] = field(default_factory=list)
        self.timestamp = -1

    def load(self) -> bool:
        pass

    def _is_loaded(self) -> bool:
        if not self.loaded:
            vprint("Unable to perform operation on log object as it has not been loaded.")
            return True
        return False

    def export(self):
        if not self._is_loaded(): return None

class LogManager:
    def __init__(self, container):
        self.container = container

    async def update_log(self) -> bool: # maybe accept a list later
        current_day = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()) # normalised

        found: ReturnData = await self.container.database.read_one("SELECT * FROM logs WHERE timestamp = ?", (current_day,))
        if not found.success:
            vprint("Error when checking for existing logs by timestamp.")
            return False
        
        if found.data != None:
            return False
        
        write: ReturnData = await self.container.database.write("INSERT INTO logs (timestamp) VALUES (?)",(current_day,))
        if not write.success:
            vprint("Error when creating new log object.")
            return False
        
        vprint("Successfully created new log object.")
        return True
    
    def get_log(self, index: int = 0) -> ReturnData:
        pass

    async def get_logs(self, index: int = 0, count: int = 10) -> ReturnData:
        found: ReturnData = await self.container.database.read_all("SELECT * FROM logs ORDER BY timestamp DESC LIMIT ? OFFSET ?",(count, index))
        if not found.success:
            return ReturnData()
        
        for index, log in enumerate(found.data):
            found_count: ReturnData = await self.container.database.read_all("SELECT COUNT(*) as count FROM readings WHERE timestamp >= ? AND timestamp < ?",(log["timestamp"], log["timestamp"] + 24 * 60 * 60))
            if found_count.success:
                found.data[index]["count"] = found_count.data[0]["count"]

        #print(found.data)

        return ReturnData(found.data, True)
    
    async def delete_log(self, log_id: int) -> ReturnData:
        found: ReturnData = await self.container.database.write("SELECT * FROM logs WHERE timestamp = ?",(log_id,))
        if not found.success:
            vprint("Error when deleting log. Log not found.")
            return ReturnData()
        vprint("Found log.")
        
        delete_log: ReturnData = await self.container.database.write("DELETE FROM logs WHERE timestamp = ?",(log_id,))
        if not delete_log.success:
            vprint("Error when deleting log.")
            return ReturnData()
        vprint("Successfully deleted log.")

        delete_data: ReturnData = await self.container.database.write("DELETE FROM readings WHERE timestamp >= ? AND timestamp < ?",(log_id, log_id + (60 * 60 * 24),))
        if not delete_data.success:
            vprint("Error when deleting log.")
            return ReturnData()
        vprint("Successfully deleted data for log duration.")

        return ReturnData(success=True)

    async def get_total_log_count(self) -> ReturnData:
        return await self.container.database.read_all("SELECT COUNT(*) as count FROM logs")
    
    async def get_latest_log_id(self) -> ReturnData:
        return await self.container.database.read_one("SELECT timestamp FROM logs ORDER BY timestamp DESC LIMIT 1")
