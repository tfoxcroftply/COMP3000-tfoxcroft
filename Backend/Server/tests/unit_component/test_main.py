# main unit/component testing file

import pytest
from asyncio import run_coroutine_threadsafe, wrap_future
from components.types import ReturnData
from components.data_utils import DataObject

#async def get_node_list(self) -> ReturnData:
#async def retrieve_data(self, requested_time: int, node_hwid: int | None = None, type: DataTypeEnum = DataTypeEnum.ALL, starts_from: int | None = None) -> DataObject | None: # time is in mins. maybe add some sort of caching later. DOES NOT RETURN HWID

async def test_get_node_list(container):
    future = run_coroutine_threadsafe(container.node_manager.get_node_list(), container.loop)
    response = await wrap_future(future)
    assert isinstance(response, ReturnData)
    assert isinstance(response.data, list)

@pytest.mark.xfail(reason="Requires active bridge connection")
def test_is_connected(container):
    assert container.node_manager.node_receiver.bridge.is_connected() == True

async def test_get_readings(container):
    future = run_coroutine_threadsafe(container.data_utils.retrieve_data(60), container.loop)
    response = await wrap_future(future)
    assert isinstance(response, DataObject)

async def test_get_logs(container):
    future = run_coroutine_threadsafe(container.logs.get_logs(), container.loop)
    response = await wrap_future(future)
    assert isinstance(response, ReturnData)
    assert isinstance(response.data, list)

async def test_get_thresholds(container):
    future = run_coroutine_threadsafe(container.thresholds.get_all(), container.loop)
    response = await wrap_future(future)
    assert isinstance(response, ReturnData)
    assert isinstance(response.data, list)

async def test_get_notifications(container):
    future = run_coroutine_threadsafe(container.notifications.get_notification_list(), container.loop)
    response = await wrap_future(future)
    assert isinstance(response, ReturnData)
    assert isinstance(response.data, list)