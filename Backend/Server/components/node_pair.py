# handled by node_manager
# pairing sequence and websocket

# api request starts the websocket function
# the interface connects to the websocket
# websocket turns off after 30 seconds

import websockets
from asyncio import create_task, sleep, CancelledError
from time import time

from components.serial import NodeSerial
from components.print import vprint
from components.types import ReturnData, NodeSerialData

class NodePair:
    def __init__(self, container):
        self.container = container
        self._websocket_active: bool = False
        self._websocket = None
        self._pairing_active: bool = False # needs a check because multiple instances of the websocket handler can spawn
        self._serial = NodeSerial(container)
        self._serial.start(self.container.config.usb_port, "tnn")
        self._last_activity: int = -1

    async def _pairing_sequence(self, websocket):
        # while true do print stuff from serial module command list
        if self._pairing_active: 
            await websocket.close()
            return

        try:
            await websocket.send("Connecting to serial.")
            await websocket.send("Attempting to connect to node. Ensure the node is plugged into the hub.")
            for i in range(10): # temporary

                self._serial.send_command("tnh:connect:\n")
                data: NodeSerialData | None = self._serial.receive_command()
                if data:
                    await websocket.send("Recieved node pairing information.")
                    self._serial.send_command("tnh:paired:\n")

                    added: ReturnData = await self.container.node_manager.add_node(data.command)
                    if added.success:
                        await websocket.send("Successfully paired node. Refreshing in 5 seconds.")
                        await sleep(5)
                        await websocket.send("refresh")
                    else:
                        error: str = f"Unable to pair to node. {"Error unknown." if added.data is None else added.data}"
                        await websocket.send(error)
                        vprint(error, error=True)

                    break

                await sleep(1)
            else:
                await websocket.send("Pairing failed. No node was detected.")

            # connect to node

        except websockets.ConnectionClosed:
            vprint("Websocket closed by command.")
        except Exception as e:
            vprint(f"Websocket error. '{e}'", error=True)
        finally:
            self._pairing_active = False
            await websocket.close()

    def is_active(self) -> bool:
        return self._websocket_active

    async def connect(self) -> bool:
        if self._websocket_active :
            vprint("Websocket failed to open. Websocket is already active and pending closure.", error=True)
            return
        
        try:        
            self._websocket_active = True
        
            self._serial.message_list = []
            self._last_activity = time()

            self._websocket = await websockets.serve(handler=self._pairing_sequence, host="127.0.0.1", port=self.container.config.websocket_port, origins=["http://localhost:5173"])
            vprint("Websocket listening.")

            try:
                while time() - self._last_activity < self.container.config.websocket_timeout:
                    await sleep(1)
                vprint("Websocket timed out.")
            except CancelledError:
                vprint("Websocket terminated due to request.")
            finally:
                vprint("Websocket closing.")
                self._websocket.close()

        finally:
            self._websocket_active = False

        return
    
