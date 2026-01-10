class _Config:
    def __init__(self):
        self.debug = False
        self.serial_debug = True

class Container:
    def __init__(self):
        self.config = _Config()