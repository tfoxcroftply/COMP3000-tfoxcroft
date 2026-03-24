from dataclasses import dataclass, field
from time import time

from components.types import ReturnData, DataBlock, DataTypeEnum
from components.print import vprint
from components.node_manager import Node

@dataclass(slots=True)
class DataObject:
    data: list[DataBlock]
    time: int # time range minutes
    type: DataTypeEnum = DataTypeEnum.ALL

    def _check_for_single_target(self, target_type: DataTypeEnum) -> bool:
        if target_type == DataTypeEnum.ALL:
            vprint("Calculation of average values requires a single target data type.")
            return False
        
        return True

    def get_average(self, target_type: DataTypeEnum) -> float | None:
        if not self._check_target(target_type): return None
        
        vprint("Calculating average readings for data object.")
        
        current_total: float | None = None
        current_count: int = 0

        for entry in self.data:
            current_total += entry.temperature if target_type == DataTypeEnum.TEMPERATURE else entry.humidity
            current_count += 1

        if current_count > 0:
            vprint("Successfully calculated average of data object values.")
            return current_total / current_count
        
        vprint("Unable to calculate average of readings. No valid readings found.")
        return None

    def get_max(self, target_type: DataTypeEnum) -> ReturnData:
        if not self._check_for_single_target(target_type): return ReturnData()

        temp_list: list[float] = []

        for entry in self.data:
            temp_list.append(entry.temperature if target_type == DataTypeEnum.TEMPERATURE else entry.humidity)

        if len(temp_list) > 0:
            return ReturnData(max(temp_list), True)
        
        vprint("Unable to calculate maximum value of readings. No valid readings found.")
        return ReturnData(success=True)

    def get_min(self, target_type: DataTypeEnum) -> ReturnData:
        if not self._check_for_single_target(target_type): return ReturnData()

        temp_list: list[float] = []

        for entry in self.data:
            temp_list.append(entry.temperature if target_type == DataTypeEnum.TEMPERATURE else entry.humidity)

        if len(temp_list) > 0:
            return ReturnData(min(temp_list), True)
        
        vprint("Unable to calculate minimum value of readings. No readings found.")
        return ReturnData(success=True)
    
    def get_std_dev(self, target_type: DataTypeEnum) -> ReturnData: # not sure if this will be used
        pass

class DataUtils:
    def __init__(self, container):
        self.container = container

    async def retrieve_data(self, requested_time: int, node_hwid: int | None, type: DataTypeEnum = DataTypeEnum.ALL) -> DataObject | None: # time is in mins. maybe add some sort of caching later. DOES NOT RETURN HWID
        # add validation for time here later

        current_time = int(time())

        found: ReturnData

        if node_hwid is not None:
            found = await self.container.database.read_all(f"SELECT * from readings WHERE node_hwid = ? AND timestamp <= ? AND timestamp >= ?",(node_hwid ,current_time, current_time - requested_time * 60,))
        else:
            found = await self.container.database.read_all(f"SELECT * from readings WHERE timestamp <= ? AND timestamp >= ?",(current_time, current_time - requested_time * 60,))

        if found.success:
            collected_data: list[DataBlock] = []
            for row in found.data:
                found_temp = row["temp"] if (type == DataTypeEnum.ALL or type == DataTypeEnum.TEMPERATURE) else None
                found_hum = row["hum"] if (type == DataTypeEnum.ALL or type == DataTypeEnum.HUMIDITY) else None

                new_data = DataBlock(row["timestamp"], found_temp, found_hum, node_hwid if node_hwid is None else None)
                collected_data.append(new_data)

            count = len(collected_data)
            if count > 0:
                vprint(f"Retrieved {count} reading{"s" if count > 1 else ""} from database.")
            else:
                vprint("No readings found in database.")
                
            return DataObject(collected_data, requested_time, type)
        
        vprint("Unable to retrieve data readings from database.")
        return None
    
    async def combine_data(self, data: DataObject) -> DataObject | None:
        pass
    
    def get_type_from_string(self, target_type: str) -> DataTypeEnum | None:
        types = {"all": DataTypeEnum.ALL, "temp": DataTypeEnum.TEMPERATURE, "hum": DataTypeEnum.HUMIDITY}

        return types.get(target_type)