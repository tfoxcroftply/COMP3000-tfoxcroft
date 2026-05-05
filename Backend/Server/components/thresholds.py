# for managing thresholds and other related information

from time import time
from components.print import vprint
from components.types import ReturnData, ThresholdData, DataBlock, NotificationType

class Thresholds:
    def __init__(self, container):
        self.container = container

    async def _threshold_trigger(self, data: DataBlock, threshold: dict) -> bool:
        # further checks
        if threshold["triggered"] == 1:
            return False

        write: ReturnData
        in_cooldown = False

        if threshold["last_trigger"] > int(time()) - self.container.config.threshold_cooldown * 60:
            write = await self.container.database.write("UPDATE thresholds SET triggered = ? WHERE id = ?", (1, threshold["id"]))
            in_cooldown = True
        else:
            write: ReturnData = await self.container.database.write("UPDATE thresholds SET triggered = ?, last_trigger = ? WHERE id = ?", (1, int(time()), threshold["id"]))

        # update threshold
        if not write.success:
            vprint("Failed to trigger threshold.")
            return False

        if in_cooldown:
            vprint("Threshold triggered but is still in cooldown. No notification sent.")
            return True
        
        vprint("Threshold triggered.")

        # find node
        node = "?"

        found_node: ReturnData = await self.container.database.read_one("SELECT * FROM nodes WHERE hwid = ? LIMIT 1",(data.node_hwid,))
        if found_node.success:
            if found_node.data is not None:
                if found_node.data["name"] is not None:
                    node = found_node.data["name"]
        else:
            vprint("Error when searching for node by HWID.")

        # send message
        message = f"Threshold '{threshold["name"]}' has been triggered by {node}. Current value of {data.temp:.2f}°C {"exceeds" if threshold["threshold_type"] == "greater_than" else "is below"} threshold value of {threshold["value"]:.2f}°C."
       
        await self.container.sms.send_message("TemperatureNet: " + message.replace("°","")) # remove decimal places just in case

        if threshold["active_notify_id"] is not None:
            await self.container.notifications.delete(threshold["active_notify_id"]) # chose not to check for success

        new_notify: ReturnData = await self.container.notifications.add(message, NotificationType.WARN, True)
        if new_notify.success and new_notify.data != None:
            update: ReturnData = await self.container.database.write("UPDATE thresholds SET active_notify_id = ? WHERE id = ?", (new_notify.data, threshold["id"]))
            if not update.success:
                vprint("Failed to update threshold notification information.")
                return False

        return True
    
    async def _threshold_trigger_remove(self, threshold: dict) -> bool:
        write: ReturnData = await self.container.database.write("UPDATE thresholds SET triggered = 0 WHERE id = ?",(threshold["id"],))
        if write.success:
            vprint("Successfully cleared threshold trigger state.")
            return True
        
        vprint("Error when clearing threshold trigger state.")
        return False
    
    async def _remove_unused_notifications(self): # may not need this
        found_thresholds: ReturnData = await self.container.database.read_all("SELECT * FROM thresholds")
        found_notifications: ReturnData = await self.container.database.read_all("SELECT * FROM notifications")

        if not found_thresholds.success or not found_notifications.success:
            vprint("Failed to check for unused notifications.")
            return

        unused_notifications: list[dict] = [
            notification for notification in found_notifications.data if notification["text"].startswith("Threshold") # maybe add source property later
        ]

        for threshold in found_thresholds.data:
            if threshold["triggered"] == 0: continue

            for notification in unused_notifications[:]:
                if threshold["active_notify_id"] == notification["id"]:
                    unused_notifications.remove(notification)

        for old_notification in unused_notifications:
            write: ReturnData = await self.container.database.write("DELETE FROM notifications WHERE id = ?",(old_notification["id"],))
            if not write.success:
                vprint("Failed to delete unused threshold notification.")
                continue

            vprint("Deleted unused threshold notification.")
            

    async def calculate_thresholds(self, data: list[DataBlock]) -> bool:
        current_thresholds: ReturnData = await self.container.database.read_all("SELECT * FROM thresholds WHERE enabled = 1")
        if current_thresholds.success == False: 
            vprint("Failed to retrieve thresholds information.")
            return False

        for entry in data: # probably a more efficient way to do this, check later
            for threshold in current_thresholds.data:
                if threshold["enabled"] == 0:
                    continue
                if (entry.temp >= threshold["value"] and threshold["threshold_type"] == "greater_than") or (entry.temp <= threshold["value"] and threshold["threshold_type"] == "less_than"):
                    await self._threshold_trigger(entry, threshold)
                elif threshold["triggered"] == 1:
                    await self._threshold_trigger_remove(threshold)

        await self._remove_unused_notifications()

        # threshold_type: str | None = None
        # value: int | None = None

        return True

    async def get(self, id: int | None) -> ReturnData:
        return await self.container.database.read_one("SELECT * FROM thresholds WHERE id = ? LIMIT 1", (id,))

    async def get_all(self) -> ReturnData:
        data: ReturnData = await self.container.database.read_all("SELECT * FROM thresholds")
        if data.success:
            return ReturnData(data.data, True)
        
        vprint("Unable to retrieve thresholds.")
        return ReturnData()

    async def get_alert_count(self) -> ReturnData:
        data: ReturnData = await self.container.database.read_all("SELECT COUNT(*) as count FROM thresholds WHERE triggered = 1")
        if data.success:
            return ReturnData(data.data, True)

        return ReturnData("Unable to retrieve triggered thresholds.")
    
    def _validate(self, data: ThresholdData) -> ReturnData:
        if len(data.name) > 30:
            return ReturnData("Name is too long.")
        
        if data.threshold_type != "greater_than" and data.threshold_type != "less_than":
            return ReturnData("Threshold type invalid.")
        
        if data.value > 50 or data.value < -10:
            return ReturnData("Temperature range invalid. Must be between -10°C and 50°C.")
        
        return ReturnData(success=True)
    
    async def create(self, data: ThresholdData) -> ReturnData:
        vprint("Creating threshold.")

        validation: ReturnData = self._validate(data)
        if not validation.success:
            return ReturnData(validation.data)

        matching: ReturnData = await self.container.database.read_one("SELECT * FROM thresholds WHERE (threshold_type, value) = (?, ?)", (data.threshold_type, data.value))
        if matching.success:
            if matching.data:
                vprint("Failed to create threshold. Identical threshold already exists.")
                return ReturnData("Identical threshold already exists.")

            create: ReturnData = await self.container.database.write("INSERT INTO thresholds (name, threshold_type, value, enabled, triggered) VALUES (?, ?, ?, ?, ?) RETURNING id", (data.name or "Threshold", data.threshold_type, data.value, data.enabled, 0), True)
            if create.success:
                vprint("Succesfully created threshold.")
                return ReturnData(create.data[0], True)

        vprint("Error when creating threshold.")
        return ReturnData("Error when creating threshold.")
    
    async def update(self, data: ThresholdData) -> ReturnData:
        vprint("Updating threshold.")
        validation: ReturnData = self._validate(data)
        if not validation.success:
            return ReturnData(validation.data)
        
        found: ReturnData = await self.container.database.read_one("SELECT * FROM thresholds WHERE id = ?",(data.id,))
        if not found.success:
            temp = "Failed to search for existing threshold."
            vprint(temp, True)
            return ReturnData(temp)

        if not found.data:
            temp = "Threshold does not exist."
            vprint(temp, True)
            return ReturnData(temp)

        write: ReturnData = await self.container.database.write("UPDATE thresholds set name = ?, threshold_type = ?, value = ?, enabled = ? WHERE id = ?",(data.name, data.threshold_type, data.value, data.enabled, data.id))
        if write.success:
            return ReturnData(success=True)
        
        temp = "Failed to update threshold."
        vprint(temp)
        return ReturnData(temp)
    
    async def delete(self, id: int) -> ReturnData:
        vprint("Deleting threshold.")

        found: ReturnData = await self.container.database.read_one("SELECT * FROM thresholds WHERE id = ?",(id,))
        if not found.success:
            temp = "Failed to delete threshold. Existing threshold check failed."
            vprint(temp)
            return ReturnData(temp)
        
        if len(found.data) == 0:
            temp = "Failed to delete threshold. Threshold does not exist."
            vprint(temp)
            return ReturnData(temp)
        
        delete: ReturnData = await self.container.database.write("DELETE FROM thresholds WHERE id = ?",(id,))
        if not delete.success:
            temp = "Failed to delete threshold."
            vprint(temp)
            return ReturnData(temp)
        
        if found.data["active_notify_id"] is not None:
            notify_found: ReturnData = await self.container.database.read_one("SELECT * FROM notifications WHERE id = ?",(found.data,))
            if notify_found.success:
                if len(notify_found.data) > 0:
                    notify_delete: ReturnData = await self.container.database.write("DELETE FROM notifications WHERE id = ?",(found.data["active_notify_id"],))
                    if notify_delete.success:
                        vprint("Successfully deleted leftover threshold notification.")
                    else:
                        vprint("Failed to delete leftover notification from deleted threshold.")
            else:
                vprint("Failed to search for leftover notifications from deleted threshold.")

        vprint("Successfully deleted threshold.")
        return ReturnData(success=True)



