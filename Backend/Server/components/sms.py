# untested

from components.print import vprint
from components.types import ReturnData

from gsmmodem.modem import GsmModem

class SMS:
    def __init__(self, container):
        self.container = container
        self.modem = GsmModem(self.container.config.sms_port, self.container.config.usb_baud)
        self._started = False

    def _check_status(self) -> bool:
        if self._started and self.modem.alive:
            return True
        
        vprint("SMS module has not been started and/or module is disconnected.", error=True)
        return False

    def start(self) -> bool:
        if self.container.config.sms_port == None:
            vprint("SMS module cannot start. Config has no port defined.", error=True)
            return False
        
        if self._check_status():
            return False

        try:
            self.modem.connect() # maybe use pin code later
            if self.modem.alive: # not sure what this actually means, check docs and test later
                return True
        except Exception as e:
            vprint(f"Failed to start SMS module: '{e}'", error=True)

        return False
    
    async def get_recipient(self) -> ReturnData:
        if not self._check_status(): return ReturnData()
        return await self.container.database.read_one("SELECT * FROM sms LIMIT 1")
    
    def set_recipient(self, number_string: str) -> ReturnData:
        if not self._check_status(): return ReturnData()

        if not len(str(number_string)) > 10:
            return ReturnData("Provided phone number is too short.")
        
        return ReturnData()
    
    async def send_message(self, message: str) -> ReturnData:
        if not self._check_status(): return ReturnData()

        found: ReturnData = await self.get_recipient()
        if not found.data and found.success:
            return ReturnData("No phone number saved.")

        return ReturnData()

    def get_signal(self) -> float | None: # maybe from 0-100% or dBm
        if not self._check_status(): return None
        
        return self.modem.signalStrength or None