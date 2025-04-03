from queue import SimpleQueue
import logging
import threading

from mining_sim.nodes.base import SimulationNode
from mining_sim.enums.sim_enums import UnloadStationState as StationState


logger = logging.getLogger(__name__)


class UnloadQueue(SimpleQueue):
    """Unload queue class"""

    def __init__(self, station_id: int):
        """Constructor for UnloadQueue class"""
        super().__init__()
        self._lock = threading.Lock()
        self.station_id: int = station_id

    def __str__(self):
        return f"Q-Station-ID-{self.station_id}"

    def put_truck(self, item):
        """Put an item into the queue"""
        with self._lock:
            self.put(item)

    def queue_size(self):
        """Get the current queue size"""
        with self._lock:
            return self.qsize()

    def get_truck(self):
        """Get an item from the queue"""
        with self._lock:
            if self.empty():
                return None
            return self.get()


class UnloadingStation(SimulationNode):
    """Class for simulating an unloading station"""

    def __init__(self, station_id: int):
        """Constructor for unloading station class

        Args:
            station_id (int): Station ID of the specified unloading station
        """
        logger.debug("Initializng unloading site")
        super().__init__(idx=station_id, node_type="UnloadStation")
        self._state = StationState.Unoccupied
        """State of the unloading station"""
        self.unloading_truck_id: int = None
        """Truck ID that is currently unloading at the station"""
        self.unload_queue = UnloadQueue(station_id)
        """Queue object to process incoming trucks"""

    def _next_state(self):
        """Evaluate next state of the station"""
        # TODO: Implement in future versions
        pass

    def get_wait_time(self):
        """Get the total wait time based on mining truck at any given time"""
        # Since each sim clock tick is 5 minutes, for every tick
        # one mining truck can complete the unloading operation

        # Okay to use qsize here as threading.lock has been implemented
        return 1 * self.unload_queue.queue_size()

    def log_data(self, truck_dequeued: int):
        """Log data for the unloading station class

        Args:
            truck_dequeued (int) : Truck dequeued in the current tick
        """
        _data = {
            "tick": self.current_tick,
            "id": self.idx,
            "truck_unloading": truck_dequeued,
            "wait_time": self.get_wait_time(),
        }

        self._data_log_list.append(_data)

    # Instead of passing the entire truck object into the queue,
    # simply pass the truck_id into the queue
    def tick(self, trucks: list[int] = []) -> int:
        """Tick function for station: Update the unload queue by inserting the truck passed in as argument
        and removing the first truck in the queue (FIFO)

        Args:
            trucks (list[int]): Pass Truck IDs to insert into queue.
                None indicates no new trucks are inserted.

        Returns:
            int: Truck ID removed from queue (FIFO)
        """
        # Increment time step
        self.current_tick += 1

        # Insert new truck into the   queue
        if trucks:
            for truck in trucks:
                self.unload_queue.put_truck(truck)
            logger.debug(f"{self}: At T={self.current_tick}:, Number of trucks inserted: {len(trucks)}")

        # Pop theleft-most truck from queue
        # This represents a truck completing unload operation, representing one tick
        _truck_dequeued = self.unload_queue.get_truck()
        if _truck_dequeued:
            logger.debug(f"{self}: At T={self.current_tick}: Truck ID finished unloading: {_truck_dequeued}")

        # Log data each tick
        self.log_data(_truck_dequeued)

        return _truck_dequeued
