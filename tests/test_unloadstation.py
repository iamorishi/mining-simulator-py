import logging
import pytest

from mining_sim.nodes.unloadstation import UnloadingStation

logger = logging.getLogger(__name__)


@pytest.fixture
def setup():
    """Setup function for unload station test cases"""
    station = UnloadingStation(station_id=1)

    return station


@pytest.mark.skip(reason="Function is not yet implemented")
def test_station_next_state(setup):
    """Test function to verify next_state function of station"""
    # TODO: Implement when next_state function is implmented

    assert True


def test_station_tick(setup: UnloadingStation):
    """Test function for unload station tick"""
    station: UnloadingStation = setup
    logger.debug("Testing initial conditions for station")
    # Verify queue is empty at the start and we are not serving any trucks
    assert station.get_wait_time() == 0
    assert station.unloading_truck_id is None

    # Insert some trucks into queue by calling tick
    logger.debug("Process one tick at a time of station node")
    truck_list = [1, 5, 13, 17, 25, 12]
    _wait_time = len(truck_list) - 1

    assert station.tick(trucks=truck_list) == 1
    assert station.get_wait_time() == _wait_time

    for truck in truck_list[1:]:
        assert station.tick() is truck
        _wait_time -= 1
        assert station.get_wait_time() == _wait_time

    # Process another tick
    assert station


# NOTE: Add remaining test cases for station class below:
