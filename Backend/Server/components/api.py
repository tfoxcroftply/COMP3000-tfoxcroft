import logging
import threading
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from asyncio import create_task
import uvicorn
from components.print import vprint

from components.types import ReturnData

class Api:
    def __init__(self,container) -> None:
        self.container = container
        self.active = False

        self.api = FastAPI()
        self.api.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"], # reconsider maybe
            allow_methods=["*"],
            allow_headers=["*"],
            )

    def _add_routes(self):
        @self.api.get("/api/get-nodes")
        async def _get_nodes():
            found = await self.container.node_manager.get_node_list()
            if found.success == False:
                raise HTTPException(400, "Unable to retrieve node information.")
            
            return {"data": found.data}

        @self.api.get("/api/get-node-info")
        async def _get_node_info(node_hwid: str = Header(None, alias="node-hwid")):
            if node_hwid == "":
                raise HTTPException(400, "No input was provided.")
            
            found = await self.container.node_manager.get_node_info(node_hwid)

            if found.success == False:
                raise HTTPException(400, "Unable to retrieve node information.")
            
            if found.data == None:
                raise HTTPException(404, "Node does not exist.")
        
            return {"data": found.data}
        
        @self.api.get("/api/get-notifications")
        async def _get_notifications():
            found: ReturnData = await self.container.notifications.get_notification_list()
            if found.success == True:
                return {"data": found.data}
            
            raise HTTPException(400, "Unable to retrieve notifications.")
        
        @self.api.patch("/api/patch-notifications-read")
        async def _patch_notifications_read():
            success: bool = await self.container.notifications.set_all_to_read()
            if success == True:
                return True
        
            raise HTTPException(400, "Unable to set all notifications to read.")
    
        @self.api.get("/api/health")
        async def _get_health():
            return
        
        @self.api.post("/api/websocket-start")
        async def _websocket_begin():
            create_task(self.container.node_manager.node_pair.connect())
            return self.container.node_manager.node_pair.is_active()

        
    def is_active(self) -> bool:
        return self.is_active

    async def start(self) -> None:
        vprint("Starting API.")

        self._add_routes()

        config = uvicorn.Config(
            self.api,
            port = 80
        )

        self.active = True

        await uvicorn.Server(config).serve()

