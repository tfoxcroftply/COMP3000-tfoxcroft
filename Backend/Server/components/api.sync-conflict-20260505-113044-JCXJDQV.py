import logging
import threading
from fastapi import FastAPI, HTTPException, Header, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from asyncio import create_task
import uvicorn

from components.print import vprint
from components.types import ReturnData, DataTypeEnum, ThresholdData
from components.data_utils import DataObject
from components.host_utils import set_system_time

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
        # nodes
        @self.api.get("/api/nodes-get")
        async def _nodes_get():
            found = await self.container.node_manager.get_node_list()
            if found.success == False:
                raise HTTPException(500, "Unable to retrieve node information.")
            
            return {"data": found.data}

        @self.api.get("/api/nodes-info")
        async def _nodes_info(node_hwid: str = Header(None, alias="node-hwid")):
            if node_hwid == "":
                raise HTTPException(400, "No input was provided.")
            
            found = await self.container.node_manager.get_node_info(node_hwid)

            if found.success == False:
                raise HTTPException(500, "Unable to retrieve node information.")
            
            if found.data == None:
                raise HTTPException(404, "Node does not exist.")
        
            return {"data": found.data}
        
        
        @self.api.patch("/api/nodes-set-info")
        async def _nodes_set_info(name: str = Body(), node_hwid: str = Body(), disabled: int = Body()):
            write: ReturnData = await self.container.node_manager.update_node(name, node_hwid, disabled)
            if (write.success):
                return True
            
            return HTTPException(400, write.data)
        
        @self.api.get("/api/notifications-get")
        async def _get_notifications():
            found: ReturnData = await self.container.notifications.get_notification_list()
            if found.success:
                return {"data": found.data}
            
            raise HTTPException(400, "Unable to retrieve notifications.")
        
        @self.api.patch("/api/notifications-read")
        async def _patch_notifications_read():
            success: bool = await self.container.notifications.set_all_to_read()
            if success:
                return True
        
            raise HTTPException(500, "Unable to set all notifications to read.")
        
        @self.api.delete("/api/notifications-delete")
        async def _delete_notifications_delete(id: int = Body()):
            success: bool = await self.container.notifications.delete(id)
            if success:
                return True
        
            raise HTTPException(500, "Unable to delete notification.")
        
        @self.api.delete("/api/notifications-delete-all")
        async def _delete_notifications_delete_all():
            success: bool = await self.container.notifications.delete_all()
            if success:
                return True
        
            raise HTTPException(500, "Unable to delete notifications.")
        
        # bridge
        @self.api.get("/api/bridge-get-connected")
        async def _get_bridge_info():
            return self.container.bridge.is_connected
        

        # thresholds
        @self.api.get("/api/thresholds-get-all")
        async def _get_thresholds():
            found: ReturnData = await self.container.thresholds.get_all()
            if found.success:
                return {"data": found.data}
            
        @self.api.get("/api/thresholds-get")
        async def _threshold_get(id: int = Header(...)):
            found: ReturnData = await self.container.thresholds.get(id)
            if found.success:
                return {"data": found.data}
            
            raise HTTPException(500, "Unable to retrieve threshold")
        
        @self.api.post("/api/thresholds-create")
        async def _threshold_create(name: str | None = Body(None), threshold_type: str = Body(...), value: int = Body(...), enabled: int = Body(...)):
            created: ReturnData = await self.container.thresholds.create(ThresholdData(name=name, threshold_type=threshold_type, value=value, enabled=enabled))
            if created.success:
                return {"id": created.data}

            raise HTTPException(500, created.data)
        
        @self.api.patch("/api/thresholds-update")
        async def _threshold_update(id: int = Body(), name: str = Body(None), threshold_type: str = Body(...), value: int = Body(...), enabled: int = Body(...)):            
            created: ReturnData = await self.container.thresholds.update(ThresholdData(id=id, name=name, threshold_type=threshold_type, value=value, enabled=enabled))
            if created.success:
                return {"id": created.data}

            raise HTTPException(500, created.data)
        
        
        @self.api.delete("/api/thresholds-delete")
        async def _threshold_delete(id: int):
            return await self.container.thresholds.delete(id)
        
        @self.api.get("/api/thresholds-alert-count")
        async def _threshold_alert_count():
            found: ReturnData = await self.container.thresholds.get_alert_count()
            if found.success:
                return found.data[0]["count"]
            
            raise HTTPException(500, found.data)

        # data
        @self.api.get("/api/readings-get/")
        async def _get_readings(duration: int, node_hwid: int | None = None, starts_from: int | None = None):
            found: DataObject = await self.container.data_utils.retrieve_data(duration, node_hwid, starts_from=starts_from)
            found.insert_blanks()

            if found is not None:
                return {"data": found.data}
            
            raise HTTPException(400, "Error when retrieving readings.")
        
        # unused
        @self.api.get("/api/readings-maximum")
        async def _get_maximum_reading(duration: int = 60, node_hwid: int | None = Header(None), target_reading: str = Query(...)):
            if target_reading is None:
                raise HTTPException(400, "Unable to calculate maximum reading. No target value provided.")
            

            target_reading: DataTypeEnum | None = self.container.data_utils.get_type_from_string(target_reading)
            if not target_reading:
                raise HTTPException(400, "Unknown target reading.")
            
            found: DataObject = await self.container.data_utils.retrieve_data(duration, node_hwid=node_hwid)

            if found is not None:
                maximum: ReturnData = found.get_max(target_reading)
                if maximum.success:
                    if maximum.data is not None: # ensure "is not None" is used, values of 0.0 will count as false
                        return maximum
                    else:
                        raise HTTPException(404, "Error when calculating maximum value of readings. No valid readings found.")
            
            raise HTTPException(500, "Error when calculating maximum value of readings.")
        
        # unused
        @self.api.get("/api/readings-minimum")
        async def _get_minimum_reading(duration: int = Query(60), node_hwid: int | None = Header(None), target_reading: str = Query(...)):
            if target_reading is None:
                raise HTTPException(400, "Unable to calculate minimum reading. No target value provided.")
            
            #debug_hwid = 111111111111

            target_reading: DataTypeEnum | None = self.container.data_utils.get_type_from_string(target_reading)
            if not target_reading:
                raise HTTPException(400, "Unknown target reading.")
            
            found: DataObject = await self.container.data_utils.retrieve_data(duration, node_hwid=node_hwid)

            minimum: ReturnData = found.get_min(target_reading)
            if minimum.success:
                if minimum.data is not None:
                    return minimum
                else:
                    raise HTTPException(404, "Error when calculating minimum value of readings. No valid readings found.")
            
            raise HTTPException(500, "Error when calculating minimum value of readings.")
        
        @self.api.get("/api/readings-frequency")
        async def _get_readings_frequency():
            return {"data": self.container.config.lora_scan_frequency}
        
        # logs
        @self.api.get("/api/logs-get")
        async def _logs_get(index: int = Body(0)):
            found: ReturnData = await self.container.logs.get_logs(index)
            count: ReturnData = await self.container.logs.get_total_log_count()
            if found.success and count.success:
                return {"data": {"logs": found.data, "total_logs": count.data[0]["count"]}}
            
            raise HTTPException(500, "Error when retrieving logs.")
        
        @self.api.get("/api/logs-get-latest-id")
        async def _logs_get_latest():
            found: ReturnData = await self.container.logs.get_latest_log_id()
            if found.success:
                return {"data": found.data}
            
            raise HTTPException(500, "Error when retrieving latest log ID.")
        
        @self.api.delete("/api/logs-delete")
        async def _logs_delete(log_id: int):
            delete: ReturnData = await self.container.logs.delete_log(log_id)
            if delete.success:
                return True
            raise HTTPException(500, "Error when deleting a log.")

        # misc
        @self.api.get("/api/health")
        async def _get_health():
            return
        
        @self.api.post("/api/websocket-start")
        async def _websocket_begin():
            create_task(self.container.node_manager.node_pair.connect())
            return self.container.node_manager.node_pair.is_active()
        
        @self.api.post("/api/system-update-time")
        async def _system_update_time(timestamp: int = Body(embed=True)):
            response: ReturnData = set_system_time(timestamp)
            if response.success:
                return True
            raise HTTPException(500, "Error when setting system time.")
        
        @self.api.patch("/api/system-set-recipient")
        async def _system_set_recipient(recipient: str = Body(embed=True)):
            response: ReturnData = await self.container.sms.set_recipient(recipient)
            if response.success:
                return True
            raise HTTPException(500, response.data)
        
        @self.api.get("/api/system-get-recipient")
        async def _system_get_recipient():
            found: ReturnData = await self.container.sms.get_recipient()
            if found.success:
                return {"recipient": found.data}
            
            raise HTTPException(500, found.data)
        
        @self.api.get("/api/system-sms-enabled")
        async def _system_sms_enable():
            write: ReturnData = await self.container.sms.is_enabled()
            if write.success:
                return write.data
            
            raise HTTPException(500, write.data)
                        
        @self.api.patch("/api/system-set-sms-enabled")
        async def _system_sms_set_enabled(enabled = Body(embed=True)):
            write: ReturnData = await self.container.sms.set_enabled(enabled)
            if write.success:
                return True
            
            raise HTTPException(500, write.data)
        

        @self.api.get("/api/system-signal")
        async def _system_signal():
            return {"signal": await self.container.sms.get_signal()}


    def is_active(self) -> bool:
        return self.active

    async def start(self) -> None:
        vprint("Starting API.")

        self._add_routes()

        config = uvicorn.Config(
            self.api,
            host="0.0.0.0", # required for local network connection
            port = 80
        )

        self.active = True

        await uvicorn.Server(config).serve()

