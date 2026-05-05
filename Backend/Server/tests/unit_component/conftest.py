# file to allow for container sharing

import pytest
import tests.unit_component.shared as shared

@pytest.fixture
def container():
    return shared.container