# handles database creation and other useful functions
# controlled by database.py

from components.print import vprint
from components.types import ReturnData

class DatabaseUtils:
    table_info = {
        "nodes": "hwid TEXT PRIMARY KEY, name TEXT NOT NULL DEFAULT 'Node', last_seen INTEGER NOT NULL DEFAULT -1, signal_strength INTEGER NOT NULL DEFAULT -1, battery_power INTEGER NOT NULL DEFAULT -1, disabled INTEGER NOT NULL DEFAULT 0, debug INTEGER NOT NULL DEFAULT 0", 
        "readings": "id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER NOT NULL, node_hwid TEXT NOT NULL, temp REAL, hum REAL, FOREIGN KEY (node_hwid) REFERENCES nodes(hwid)",
        "notifications": "id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL, timestamp INTEGER NOT NULL, notification_type INTEGER NOT NULL, read INTEGER NOT NULL DEFAULT 0",
        "thresholds": "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, threshold_type TEXT NOT NULL, value INTEGER NOT NULL, triggered INTEGER NOT NULL DEFAULT 0, last_trigger INTEGER NOT NULL DEFAULT -1, enabled INTEGER NOT NULL DEFAULT 1, active_notify_id INTEGER DEFAULT NULL, FOREIGN KEY (active_notify_id) REFERENCES notifications(id)", # 1: 1, ">=", 25, timetamp, 0
        "logs": "timestamp INTEGER PRIMARY KEY",
        "sms": "id INTEGER PRIMARY KEY AUTOINCREMENT, threshold INTEGER NOT NULL, timestamp INTEGER NOT NULL, FOREIGN KEY (threshold) REFERENCES thresholds(id)",
        "settings": "key TEXT PRIMARY KEY, value TEXT"
    }

    def __init__(self, database):
        self.database = database

    async def check_data(self):
        vprint("Checking database for existing data.")
        for table, table_schema in self.table_info.items():
            found: ReturnData = await self.database.read_one(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not found.success or found.data is None:
                vprint(f"Missing table detected: '{table}'.")
                return False
            vprint(f"Found table '{table}'.")
        
        return True

    async def create_data(self) -> bool:
        for table, table_schema in self.table_info.items():
            check: ReturnData = await self.database.read_one(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if check.success and check.data != None:
                deleted: ReturnData = await self.database.write(f"DROP TABLE {table}") # not using "IF EXISTS" for deletion tracking
                if deleted.success == False:
                    vprint(f"Failed to delete existing table '{table}'.", error=True)
                    return False
                vprint(f"Deleted existing table '{table}'.")
        
        vprint("Recreating database. " + ("'clear_database' is enabled." if self.database.container.config.clear_database else ""))

        for table, table_schema in self.table_info.items():
            written: ReturnData = await self.database.write(f"CREATE TABLE {table} ( {table_schema} )")
            if written.success == False:
                vprint("Unable to create first table in database.", error=True)
                return False

        vprint("Database successfully created.")

        if self.database.container.config.debug: # maybe just pass the container itself
            vprint("Inserting testing node information into database.")
            for i in range(self.database.container.config.debug_node_count):
                temp_name = "Node " + str(i + 1)
                found: ReturnData = await self.database.read_one("SELECT name FROM nodes WHERE name=?", (temp_name,))
                if found.success and found.data == None:
                    written: ReturnData = await self.database.write("INSERT INTO nodes (hwid, name, debug) VALUES (?, ?, ?)", (str(i + 1) * 12, temp_name, 1))
                    if written.success:
                        vprint(f"Created debug node '{temp_name}'.")
                    else:
                        vprint(f"Failed to create debug node '{temp_name}'", error=True)
        
        return True