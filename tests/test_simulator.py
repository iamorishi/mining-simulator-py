import logging
import pytest

from mining_sim.simulator import MiningSimulator, find_station_info_by_id

logger = logging.getLogger(__name__)


@pytest.fixture
def setup():
    """Setup function for simulator test cases"""
    sim = MiningSimulator(n_trucks=10, m_stations=4, stop_time_hr=25)

    return sim


def test_find_station_by_id():
    """Test function for find station info by id function"""
    station_infos = [
        {"station_id": 1, "wait_time": 2, "q_trucks": []},
        {"station_id": 2, "wait_time": 3, "q_trucks": []},
        {"station_id": 3, "wait_time": 4, "q_trucks": []},
        {"station_id": 4, "wait_time": 5, "q_trucks": []},
        {"station_id": 5, "wait_time": 6, "q_trucks": []},
        {"station_id": 6, "wait_time": 7, "q_trucks": []},
        {"station_id": 7, "wait_time": 1, "q_trucks": []},
        {"station_id": 8, "wait_time": 2, "q_trucks": []},
        {"station_id": 9, "wait_time": 3, "q_trucks": []},
        {"station_id": 10, "wait_time": 4, "q_trucks": []},
    ]

    actual_station_info = find_station_info_by_id(station_infos, 8)
    assert actual_station_info == station_infos[7]

    station_infos.sort(key=lambda x: x["wait_time"], reverse=True)
    actual_station_info = find_station_info_by_id(station_infos, 6)
    assert actual_station_info == station_infos[0]


# NOTE: This needs more unit testing, but writing a simple single unit test for now
def test_assign_station_algo(setup):
    """Test for station assignment algorithm"""
    sim = setup

    # Inputs for test
    station_infos = [
        {"station_id": 1, "wait_time": 2, "q_trucks": []},
        {"station_id": 2, "wait_time": 3, "q_trucks": []},
        {"station_id": 3, "wait_time": 4, "q_trucks": []},
        {"station_id": 4, "wait_time": 5, "q_trucks": []},
        {"station_id": 5, "wait_time": 6, "q_trucks": []},
        {"station_id": 6, "wait_time": 7, "q_trucks": []},
        {"station_id": 7, "wait_time": 1, "q_trucks": []},
        {"station_id": 8, "wait_time": 2, "q_trucks": []},
        {"station_id": 9, "wait_time": 3, "q_trucks": []},
        {"station_id": 10, "wait_time": 4, "q_trucks": []},
    ]

    new_trucks = [1, 3, 5, 7, 2, 4, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    # Run the allocation algo
    final_stations_list, final_trucks_list = sim.assign_stations_algo(new_trucks[:], station_infos)
    total_trucks_assigned = len(final_trucks_list)

    assert total_trucks_assigned == len(new_trucks)


def test_simulation_tick(setup):
    """Test function for testing one tick of the simulation"""
    # TODO: Need to add more thorough unit testing for this function.
    # It would be a good idea to break it down into smaller pieces
    # and write a unit test for each individual part
    sim = setup
    SIM_STOP = 1000
    for _ in range(SIM_STOP):
        sim.tick()

    assert sim.current_tick == SIM_STOP

    for station in sim.unloading_stations:
        logger.debug(f"Station ID: {station.idx} , Tick: {station.current_tick}")
        assert station.current_tick == SIM_STOP

    for truck in sim.mining_trucks:
        logger.debug(f"Truck ID: {truck.idx} , Tick: {truck.current_tick}")
        assert truck.current_tick == SIM_STOP
