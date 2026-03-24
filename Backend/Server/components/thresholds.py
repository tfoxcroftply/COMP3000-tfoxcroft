from components.print import vprint
from components.types import ReturnData

class Thresholds:
    def __init__(self, container):
        self.container = container

    async def get_thresholds(self) -> ReturnData:
        data: ReturnData = await self.container.database.read_all("SELECT * FROM thresholds")
        if data.success:
            return ReturnData(data.data, True)
        
        vprint("Unable to retrieve thresholds.")
        return ReturnData()

    async def get_thresholds_alert_count(self) -> ReturnData:
        data: ReturnData = await self.container.database.read_all("SELECT * FROM thresholds WHERE active_alert = ?", (1,))
        if data.success:
            return ReturnData(len(data.data), True)
        
        vprint("Unable to retrieve triggered thresholds.")
        return ReturnData()