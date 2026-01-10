import logging
import threading
from flask import Flask, Response

from components.print import vPrint

class Api:
    def __init__(self,container) -> None:
        self.container = container
        self.api = Flask(__name__)
        logging.getLogger('werkzeug').setLevel(logging.CRITICAL)

    def start(self, port: int = 80) -> None:
        vPrint("Starting API.")
        threading.Thread(target=self.api.run, kwargs={
            "port": port,
            "use_reloader": False,
            "debug": False
            }, daemon=True).start()
        vPrint(f"API started on port {port}.")
        
        @self.api.get("/api/debug")
        def node_debug():
            self.container.node_manager.debug()
            return Response("Sent node debug command.", status = 200)