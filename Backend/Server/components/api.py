import logging
import threading
from flask import Flask

from components.print import vPrint

class Api:
    def __init__(self,database) -> None:
        self.api = Flask(__name__)
        self.database = database
        logging.getLogger('werkzeug').setLevel(logging.CRITICAL)

    def start(self, port: int = 80) -> None:
        vPrint("Starting API.")
        threading.Thread(target=self.api.run, kwargs={
            "port": port,
            "use_reloader": False,
            "debug": False
            }, daemon=True).start()
        vPrint(f"API started on port {port}.")