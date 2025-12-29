import sqlite3
import os
from components.print import vPrint

class Database:
    DB_FOLDER = "data"
    DB_NAME = "database.db"

    def start(self, root_dir: str) -> None:
        vPrint("Starting database.")
        if hasattr(self,"conn") and self.conn:
            vPrint("Database already running. Initialisation request ignored.")
            return
        try:
            os.makedirs(os.path.join(root_dir,self.DB_FOLDER), exist_ok=True)
            self.conn = sqlite3.connect(os.path.join(root_dir,self.DB_FOLDER,self.DB_NAME))
            self.cursor = self.conn.cursor()
            vPrint("Database started.")
        except Exception as e:
            vPrint(f"Error during database initialisation: {e}")
            raise

    def write(self, query: str):
        pass # temporary

    def read(self, query: str):
        pass

    def delete(self, query: str):
        pass
