# integration testing for the gateway
# must be run alongside the server instance

import requests

URL = "http://temperaturenet.local"

def test_nodes_get():
    response = requests.get(URL + "/api/nodes-get/")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert isinstance(data["data"], list)

    
def test_notifications_get():
    response = requests.get(URL + "/api/notifications-get/")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert isinstance(data["data"], list)

def test_thresholds_get_all():
    response = requests.get(URL + "/api/thresholds-get-all/")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert isinstance(data["data"], list)

def test_readings_get():
    response = requests.get(URL + "/api/readings-get/", params={"duration": 60})

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert isinstance(data["data"], list)

def test_logs_get():
    response = requests.get(URL + "/api/logs-get/")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert isinstance(data["data"], dict)