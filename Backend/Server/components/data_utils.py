# retrieves data readings, providing useful functions

from dataclasses import dataclass, field
from time import time

from components.types import ReturnData, DataBlock, DataTypeEnum
from components.print import vprint
from components.node_manager import Node

class DataObject:
    def __init__(self, container, data: list[DataBlock], timestamp: int, datatype: DataTypeEnum):
        self.container = container

        self.data = data
        self.timestamp = timestamp
        self.type = datatype

    def _check_for_single_target(self, target_type: DataTypeEnum) -> bool:
        if target_type == DataTypeEnum.ALL:
            vprint("Calculation of average values requires a single target data type.")
            return False
        
        return True
    
    def insert_blanks(self) -> None:
        new_table: list[DataBlock] = []
        last_seen: dict[str, DataBlock] = {}

        for entry in self.data:
            previous = last_seen.get(entry.node_hwid)
            if previous is not None:
                if entry.timestamp - previous.timestamp > self.container.config.lora_scan_frequency * 60:
                    new_blank = DataBlock(entry.timestamp - 30, None, None, entry.node_hwid)
                    new_table.append(new_blank)

            new_table.append(entry)
            last_seen[entry.node_hwid] = entry

        self.data = new_table

    def get_average(self, target_type: DataTypeEnum) -> float | None:
        if not self._check_for_single_target(target_type): return None
        
        vprint("Calculating average readings for data object.")
        
        current_total: float | None = None
        current_count: int = 0

        for entry in self.data:
            current_total += entry.temp if target_type == DataTypeEnum.TEMPERATURE else entry.hum
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
            temp_list.append(entry.temp if target_type == DataTypeEnum.TEMPERATURE else entry.hum)

        if len(temp_list) > 0:
            return ReturnData(max(temp_list), True)
        
        vprint("Unable to calculate maximum value of readings. No valid readings found.")
        return ReturnData(success=True)

    def get_min(self, target_type: DataTypeEnum) -> ReturnData:
        if not self._check_for_single_target(target_type): return ReturnData()

        temp_list: list[float] = []

        for entry in self.data:
            temp_list.append(entry.temp if target_type == DataTypeEnum.TEMPERATURE else entry.hum)

        if len(temp_list) > 0:
            return ReturnData(min(temp_list), True)
        
        vprint("Unable to calculate minimum value of readings. No readings found.")
        return ReturnData(success=True)
    
    #def get_std_dev(self, target_type: DataTypeEnum) -> ReturnData: # not sure if this will be used
    #    pass

class data_utils:
    def __init__(self, container):
        self.container = container

    async def retrieve_data(self, requested_time: int, node_hwid: int | None = None, type: DataTypeEnum = DataTypeEnum.ALL, starts_from: int | None = None) -> DataObject | None: # time is in mins. maybe add some sort of caching later. DOES NOT RETURN HWID
        # add validation for time here later

        if starts_from is not None:
            start_time = starts_from
            end_time = starts_from + requested_time * 60 * 60
        else:
            end_time = int(time())
            start_time = end_time - requested_time * 60 * 60

        found: ReturnData

        if node_hwid is not None:
            found = await self.container.database.read_all(f"SELECT * from readings WHERE node_hwid = ? AND timestamp >= ? AND timestamp < ?",(node_hwid, start_time, end_time))
        else:
            found = await self.container.database.read_all(f"SELECT * from readings WHERE timestamp >= ? AND timestamp < ?",(start_time, end_time))

        if found.success:
            collected_data: list[DataBlock] = []
            for row in found.data:
                found_temp = row["temp"] if (type == DataTypeEnum.ALL or type == DataTypeEnum.TEMPERATURE) else None
                found_hum = row["hum"] if (type == DataTypeEnum.ALL or type == DataTypeEnum.HUMIDITY) else None
                found_node_hwid = row["node_hwid"] # retrieve anyway for other functions

                new_data = DataBlock(row["timestamp"], found_temp, found_hum, found_node_hwid) # fixed inverted logic
                collected_data.append(new_data)

            count = len(collected_data)
            if count > 0:
                vprint(f"Retrieved {count} reading{'s' if count > 1 else ''} from database.")
            else:
                vprint("No readings found in database.")
                
            return DataObject(self.container, collected_data, requested_time, type)
        
        vprint("Unable to retrieve data readings from database.")
        return None
    
    async def combine_data(self, data: DataObject) -> DataObject | None:
        pass
    
    def get_type_from_string(self, target_type: str) -> DataTypeEnum | None:
        types = {"all": DataTypeEnum.ALL, "temp": DataTypeEnum.TEMPERATURE, "hum": DataTypeEnum.HUMIDITY}

        return types.get(target_type)