from enum import Enum, auto
from dataclasses import field, dataclass
from time import time

from components.print import vprint
from components.types import ReturnData, NotificationType

@dataclass(frozen=True, slots=True)
class Notification: # maybe scrap this
    id: int
    text: str
    notify_type: NotificationType = NotificationType.GENERAL

class Notifications:
    def __init__(self, container):
        self.container = container
        self.current_list: list[NotificationType] = field(default_factory=list)

    async def get_notification_from_string(self, text: str) -> Notification | None: # if a duplicate then the latest should return (not tested)
        read: ReturnData = await self.container.database.read_one("SELECT * FROM notifications WHERE text = (?)",(text,))
        if read.success:
            if read.data == None:
                vprint("Failed to get notification from string. Matching notification does not exist.", error=True)
                return None
            
            new_notification = Notification(read.data["id"], read.data["text"], read.data["notification_type"])
            return new_notification

        vprint("Failed to get notification from string.", error=True)
        return None
    
    async def get_notification_list(self) -> ReturnData:
        #print(self.container.config.max_notifications_to_send)
        read: ReturnData = await self.container.database.read_all("SELECT * FROM notifications LIMIT ?",(self.container.config.max_notifications_to_send,)) # decided to use params
        if read.success:
            return ReturnData(read.data, True) # should be list
        
        return ReturnData()
    
    async def check_duplicate(self, text: str) -> bool:
        found: Notification = await self.get_notification_from_string(text)
        if found != None:
            return True
        
        return False
    
    async def set_all_to_read(self) -> bool:
        update: ReturnData = await self.container.database.write("UPDATE notifications SET read = (?)",(1,))

        if update.success:
            vprint("Successfully updated all notifications as read.")
            return True
        
        vprint("Unable to update all notifications as read.")
        return False
    
    async def add(self, text: str, notification_type: NotificationType = NotificationType.GENERAL, overwrite: str = False) -> bool: # return notification object later
        #read = await self.container.database.read_one("SELECT * FROM notifications WHERE text = ?", (text,))

        #if overwrite == False and (read.success and read.data != None): # allowing duplicates now
        #   vprint("Failed to add notification. Notification already exists.")
        #   return False
        
        timestamp: int = time() # float should be converted to integer here

        #print(text, timestamp, notification_type)
        write = await self.container.database.write("INSERT INTO notifications (text, timestamp, notification_type) values (?, ?, ?)", (text, timestamp, notification_type.value,))
        if write.success:
            vprint("Successfully created notification.")
            return True

        vprint("Error creating notification.", error=True)
        return False
    
    async def delete(self, id: int) -> bool:
        read: ReturnData = await self.container.database.read_one("SELECT * FROM notifications WHERE id = ?", (id,))
        if not (read.success and read.data is not None): # might be successful with no data
            vprint("Failed to remove notification. Notification does not exist.")
            return False

        write: ReturnData = await self.container.database.write("DELETE FROM notifications WHERE id = ?", (id,))
        if write.success:
            vprint("Successfully deleted notification.")
            return True
        
        vprint("Failed to delete notification.", error=True)
        return False
    
    async def delete_by_string(self, string: str) -> bool:
        found_notification: Notification | None = await self.get_notification_from_string(string)
        if found_notification is not None:
            success: bool = await self.delete(found_notification.id)
            if success:
                vprint("Successfully deleted notification by matching string.")
            else:
                vprint("Failed to delete notification by matching string. Unknown error.")
        else:
            vprint("Failed to delete notification by matching string. Notification not found.")
    

