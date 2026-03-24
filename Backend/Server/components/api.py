import logging
import threading
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from asyncio import create_task
import uvicorn

from components.print import vprint
from components.types import ReturnData, DataTypeEnum
from components.data_utils import DataObject

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
        ## nodes
        @self.api.get("/api/get-nodes")
        async def _get_nodes():
            found = await self.container.node_manager.get_node_list()
            if found.success == False:
                raise HTTPException(500, "Unable to retrieve node information.")
            
            return {"data": found.data}

        @self.api.get("/api/get-node-info")
        async def _get_node_info(node_hwid: str = Header(None, alias="node-hwid")):
            if node_hwid == "":
                raise HTTPException(400, "No input was provided.")
            
            found = await self.container.node_manager.get_node_info(node_hwid)

            if found.success == False:
                raise HTTPException(500, "Unable to retrieve node information.")
            
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
        
            raise HTTPException(500, "Unable to set all notifications to read.")
        
        ## bridge
        @self.api.get("/api/get-bridge-info")
        async def _get_bridge_info():
            return self.container.bridge.is_connected
        

        ## thresholds
        @self.api.get("/api/get-thresholds")
        async def _get_thresholds():
            found: ReturnData = await self.container.thresholds.get_thresholds()
            if found.success:
                return found.data
            
            raise HTTPException(500, "Unable to retrieve thresholds.")
        
        @self.api.get("/api/get-threshold-alert-count")
        async def _get_thresholds_alert_count():
            found: ReturnData = await self.container.thresholds.get_thresholds_alert_count()
            if found.success:
                return found.data
            
            raise HTTPException(500, "Unable to retrieve triggered thresholds.")
        

        ## data
        @self.api.get("/api/get-readings")
        async def _get_readings(duration: int = Header(60, alias="duration"), target_hwid: int = Header(None, alias="node_hwid")):
            debug_hwid = 11111111
            found: DataObject = await self.container.datautils.retrieve_data(duration, node_hwid=debug_hwid)

            if found is not None:
                return found.data
            
            raise HTTPException(400, "Error when retrieving readings.")
        
        @self.api.get("/api/get-maximum-reading")
        async def _get_maximum_reading(duration: int = Header(60, alias="duration"), target_hwid: int = Header(None, alias="node_hwid"), target_reading: str = Header(None, alias="target_reading")):
            debug_hwid = 111111111111

            if target_reading is None:
                raise HTTPException(400, "Unable to calculate maximum reading. No target value provided.")
            

            target_reading: DataTypeEnum | None = self.container.datautils.get_type_from_string(target_reading)
            if not target_reading:
                raise HTTPException(400, "Unknown target reading.")
            
            found: DataObject = await self.container.datautils.retrieve_data(duration, node_hwid=debug_hwid)

            if found is not None:
                maximum: ReturnData = found.get_max(target_reading)
                if maximum.success:
                    if maximum.data is not None: # ensure "is not None" is used, values of 0.0 will count as false
                        return maximum
                    else:
                        raise HTTPException(404, "Error when calculating maximum value of readings. No valid readings found.")
            
            raise HTTPException(500, "Error when calculating maximum value of readings.")
        

        @self.api.get("/api/get-minimum-reading")
        async def _get_minimum_reading(duration: int = Header(60, alias="duration"), target_hwid: int = Header(None, alias="node_hwid"), target_reading: str = Header(None, alias="target_reading")):
            if target_reading is None:
                raise HTTPException(400, "Unable to calculate minimum reading. No target value provided.")
            
            debug_hwid = 111111111111

            target_reading: DataTypeEnum | None = self.container.datautils.get_type_from_string(target_reading)
            if not target_reading:
                raise HTTPException(400, "Unknown target reading.")
            
            found: DataObject = await self.container.datautils.retrieve_data(duration, node_hwid=debug_hwid)

            minimum: ReturnData = found.get_min(target_reading)
            if minimum.success:
                if minimum.data is not None:
                    return minimum
                else:
                    raise HTTPException(404, "Error when calculating minimum value of readings. No valid readings found.")
            
            raise HTTPException(500, "Error when calculating minimum value of readings.")
        


        ## misc
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

