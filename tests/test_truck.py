import pytest
import logging

from mining_sim.nodes.truck import MiningTruck
from mining_sim.enums.sim_enums import TruckState

logger = logging.getLogger(__name__)


@pytest.fixture
def setup():
    """Setup function for Mining Truck Unit Tests"""
    truck = MiningTruck(truck_id=1)
    return truck


@pytest.mark.parametrize(
    "state, duration",
    [
        (TruckState.AtMine, 12),
        (TruckState.OnRoad_ToMine, 6),
        (TruckState.OnRoad_ToUnload, 6),
        (TruckState.Unloading, 1),
    ],
)
def test_state_duration(setup, state: TruckState, duration: int):
    """Test to verify correct state duration for the truck"""

    actual_duration = MiningTruck._state_duration(state)
    logger.info(f"Checking if Truck State {state.name} has the expected duration of {actual_duration} ticks")
    if state == TruckState.AtMine:
        assert actual_duration >= duration and actual_duration <= 60
    else:
        assert actual_duration == duration


def test_truck_next_state(setup):
    """Test to verify the truck progresses to next step correctly"""
    truck = setup
    logger.info(f"Truck is currently at: {truck.get_state().name}")
    # By default truck starts at mine

    truck_states = [
        TruckState.OnRoad_ToUnload,
        TruckState.Unloading,
        TruckState.OnRoad_ToMine,
        TruckState.AtMine,
    ]

    for expected_state in truck_states:
        truck._next_state()
        logger.info(f"Truck State: {truck.get_state().name} vs Expected State: {expected_state.name}")
        assert truck.get_state() == expected_state


def test_truck_tick(setup):
    """Test to verify the truck node's tick function"""
    truck = setup
    logger.info(f"Truck is currently at: {truck.get_state().name}")

    # Move from mining to on road
    truck._remaining_time_in_state = 0
    truck.tick()
    assert truck.get_state() == TruckState.OnRoad_ToUnload
    assert truck._remaining_time_in_state == 6
    assert truck.current_tick == 1

    # Spend 6 ticks to move to next state
    for _ in range(6):
        truck.tick()
        logger.debug(f"Truck {truck} - Tick {truck.current_tick} - State {truck.get_state().name}")
        logger.debug(f"Time remaining - {truck._remaining_time_in_state}")

    assert truck.get_state() == TruckState.Unloading
    assert truck._remaining_time_in_state == 1
    assert truck.current_tick == 7


# NOTE: Add remaining test cases for truck class below:
