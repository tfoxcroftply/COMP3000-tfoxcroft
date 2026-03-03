from components.node_manager import Node

class DataAnalysis:
    def __init__(self, container):
        self.container = container

    async def _check_thresholds(self):
        pass

    async def _calculate_averages(self, time: int = 1, devices: list[Node] | None = None):
        pass

    async def _calculate_all(self):
        pass