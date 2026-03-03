# rewritten - not tested yet
from __future__ import annotations

import sqlite3
import asyncio # change later to only import needed

from os.path import join, exists
from os import makedirs, remove
from typing import Any
from dataclasses import dataclass, field
from pathlib import Path
from collections.abc import Sequence

from components.print import vprint
from components.database_utils import DatabaseUtils

from components.types import DatabaseTask, ReturnData

@dataclass(frozen=True, slots=True) # not in types file, exclusive to this file
class _WriteData:
    query: str
    params: Sequence[Any] | None = None
    task: DatabaseTask | None = None

@dataclass(frozen=True, slots=True)
class _QueueData:
    write_data: _WriteData
    future: asyncio.Future[ReturnData]

class _Queue: # maybe add stop function
    def __init__(self, connection: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
        self.connection = connection
        self.cursor = cursor
        self.queue: asyncio.Queue[_QueueData] = asyncio.Queue()
        self._running = False
        self._total_changes: int = 0

    async def _loop(self) -> None:
        while True:
            queue_data = await self.queue.get()
            try:
                if queue_data.write_data.task == None:
                    vprint("Database write error: Task undefined.", error=True)
                    queue_data.future.set_result(ReturnData())
                    continue
                
                if queue_data.write_data.task == DatabaseTask.WRITE:
                    self.cursor.execute(queue_data.write_data.query, queue_data.write_data.params or ())
                    self.connection.commit()

                    changes = self.connection.total_changes
                    changed_by = changes - self._total_changes

                    if changed_by > 0:
                        vprint(f"Wrote {changed_by} line" + ("s" if changed_by > 1 else "") + " to database.")
                    else:
                        vprint(f"Wrote to database.") # creating tables doesnt count as changes

                    self._total_changes = changes

                    queue_data.future.set_result(ReturnData(success=True))

                elif queue_data.write_data.task == DatabaseTask.READ_ONE:
                    self.cursor.execute(queue_data.write_data.query, queue_data.write_data.params or ())
                    found = self.cursor.fetchone()

                    queue_data.future.set_result(ReturnData(found, True))

                elif queue_data.write_data.task == DatabaseTask.READ_ALL:
                    self.cursor.execute(queue_data.write_data.query, queue_data.write_data.params or ())
                    found = self.cursor.fetchall()

                    found_dict = [dict(row) for row in (found or [])]

                    queue_data.future.set_result(ReturnData(found_dict, True))

            except Exception as e:
                vprint(f"Database error: {e}", error=True)

            finally:
                if not queue_data.future.done():
                    queue_data.future.set_result(ReturnData())
                self.queue.task_done()
            
    async def _start(self) -> None:
        if not self._running:
            vprint("Starting database queue.")
            self._running = True
            asyncio.create_task(self._loop())

    async def schedule(self, query: str, params: Sequence[Any] | None = None, task: DatabaseTask | None = None) -> ReturnData:
        await self._start()
        
        loop = asyncio.get_running_loop()
        temp_future = loop.create_future()
        
        await self.queue.put(_QueueData(_WriteData(query, params, task), temp_future))
        return await temp_future

class Database:
    _db_folder: str = "data"
    _db_name: str = "data.db"
    _debug_db_name: str = "test.db"

    def __init__(self, container) -> None: # maybe use singleton
        self.container = container
        self.conn: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None
        self.queue: _Queue | None = None
        self._has_started: bool = False
        self.utils: DatabaseUtils = DatabaseUtils(self)

    async def start(self, root: str) -> bool:
        try:
            temp_path = Path(root)
            temp_path = join(temp_path, self._db_folder)
            makedirs(temp_path, exist_ok=True)

            temp_path = join(temp_path, self._db_name if self.container.config.debug == False else self._debug_db_name)

            vprint(f"Database path: '{temp_path}'.")

            self.conn: sqlite3.Connection | None = sqlite3.connect(temp_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor: sqlite3.Cursor | None = self.conn.cursor()
            self.queue = _Queue(self.conn, self.cursor)
            self._has_started = True

            vprint("Database started successfully.")
            
            valid: bool = await self.utils.check_data()
            if not valid or self.container.config.clear_database == True: # later fix to check for variable first before checking data entirely
                success: bool = await self.utils.create_data()
                if not success:
                    self.stop()
                    return False
                
            return True
        except Exception as e:
            self.conn, self.cursor = None, None
            vprint(f"Database initialisation failed: {e}", error=True)

        return False
    
    def stop(self) -> None:
        try:
            if self.cursor is not None:
                self.cursor.close()

            if self.conn is not None:
                self.conn.close()

            vprint("Database closed.")
        except Exception as e:
            vprint(f"Database close failed: {e}", error=True)
        
        finally:
            self.conn, self.cursor = None
            self._has_started = False

    def _check_started(self) -> bool:
        if self._has_started:
            if self.conn is not None and self.cursor is not None:
                if self._has_started == True:
                    return True
            else:
                vprint("Database connection and/or cursor missing. Closing database.", error=True)
                self.stop()
                return False

        vprint("Database command failed: database is not running.", error=True)
        return False
    
    async def write(self, query: str, params: Sequence[Any] | None = None) -> ReturnData:
        query = query.strip()
        if not (self._check_started() and query != ""): return ReturnData()

        data: ReturnData = await self.queue.schedule(query, params, DatabaseTask.WRITE)

        return data or ReturnData()

    async def read_one(self, query: str, params: Sequence[Any] | None = None) -> ReturnData: # make it run through queue later, threading issues between sqlite and flask
        query = query.strip()
        if not (self._check_started() and query != ""): return ReturnData()
        
        data: ReturnData = await self.queue.schedule(query, params, DatabaseTask.READ_ONE)
        return data or ReturnData()
    
    async def read_all(self, query: str, params: Sequence[Any] | None = None) -> ReturnData: # maybe combine with read()
        query = query.strip()
        if not (self._check_started() and query != ""): return ReturnData()

        data: ReturnData = await self.queue.schedule(query, params, DatabaseTask.READ_ALL)
        return data or ReturnData()

    def delete_one(self, query: str, params: Sequence[Any] | None) -> ReturnData: # probably can remove, just use write()
        query = query.strip()
        if not (self._check_started() and query != ""): return ReturnData()

        return ReturnData()
