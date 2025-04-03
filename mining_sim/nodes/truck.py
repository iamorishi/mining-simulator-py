import logging
import random

from mining_sim.nodes.base import SimulationNode
from mining_sim.enums.sim_enums import TruckState

logger = logging.getLogger(__name__)

# Define some global values
TRAVEL_TIME_UNLOAD_SITE_TO_MINE = 6  # Represented in ticks, 1 tick = 5 min, so 6 ticks = 30 minutes
TIME_TO_UNLOAD = 1  # Represented in ticks, 1 tick = 5 min


class MiningTruck(SimulationNode):
    """Class for simulating a mining truck"""

    def __init__(self, truck_id: int):
        """Constructor for truck_id"""
        super().__init__(idx=truck_id, node_type="Truck")
        self._state: TruckState = TruckState.AtMine  # Truck starts at the mine
        """Current status of the truck."""
        self._remaining_time_in_state: int = 6 * random.randint(2, 10)  # Assign the mining time for first iteration
        """Time remaining in current state, before transition to next state"""
        self.unload_site_id: int = -1  # -1 indicates no station assigned
        """Unloading State ID where mining truck is currently queued/docked"""
        self.unload_queued: bool = False
        """Flag to indicate whether the truck is in a queue at the Unloading station"""

    @staticmethod
    def _state_duration(state: TruckState):
        """Total duration to complete the activity in current state"""
        if state in [TruckState.OnRoad_ToMine, TruckState.OnRoad_ToUnload]:
            # Each trip on the road between mining site and unloading site
            # takes 30 minutes or 6 ticks
            return TRAVEL_TIME_UNLOAD_SITE_TO_MINE
        elif state == TruckState.AtMine:
            # Each mining activity can take any random time between 1 hour
            # and 5 hours. Randomizing this in 30-minute steps.
            # 6 ticks = 30 minutes
            return 6 * random.randint(2, 10)
        elif state == TruckState.Unloading:
            # Return 1 tick for unload activity
            return TIME_TO_UNLOAD
        else:
            # Return 0 for unloading  queue because queue time varies
            return 0

    def _next_state(self):
        """Function to evaluate the next state of mining truck"""
        # NOTE: Keeping this verbose to make it more readable
        if self.get_state() == TruckState.OnRoad_ToMine:
            self._state = TruckState.AtMine
        elif self.get_state() == TruckState.AtMine:
            self._state = TruckState.OnRoad_ToUnload
        elif self.get_state() == TruckState.OnRoad_ToUnload:
            self._state = TruckState.Unloading
        else:
            self._state = TruckState.OnRoad_ToMine
            self.unload_site_id = -1  # Indicate not a valid site ID
            self.unload_queued = False

    def assign_unload_site(self, unload_site_id: int = 0):
        """Function for assigning the mining truck to a particular unload site

        Args:
            unload_site_id (int): Unloading Site ID where the truck is routed to
        """
        logger.debug(f"{self} - Unload Site ID: {unload_site_id} - Queued: True")
        self.unload_site_id = unload_site_id
        self.unload_queued = True

    def log_data(self):
        """Log data for the truck class"""
        _state: TruckState = self.get_state()
        _data = {
            "tick": self.current_tick,
            "id": self.idx,
            "state": _state.name,
            "assigned_station": self.unload_site_id,
        }

        self._data_log_list.append(_data)

    def tick(self, unloading_complete: bool = False):
        """Function for performing required operations during one clock tick

        Args:
            unloading_complete (bool): Flag to indicate unloading is complete.
        """
        # Log data each tick
        self.log_data()

        # Increment clock tick
        self.current_tick += 1

        if self._remaining_time_in_state > 0:
            # Spend one tick in current state
            self._remaining_time_in_state -= 1

        _current_state = self.get_state()

        # Handle case where we are actively queued at an unload site
        if _current_state == TruckState.Unloading and not unloading_complete:
            return True

        if self._remaining_time_in_state == 0:
            # Move to next state
            self._next_state()
            logger.debug(
                f"{str(self)}: At T={self.current_tick}: transitioned from {_current_state.name} to {self.get_state()}"
            )
            # Reset remaining time in state to completion time for new state
            self._remaining_time_in_state = self._state_duration(self.get_state())

        return True
