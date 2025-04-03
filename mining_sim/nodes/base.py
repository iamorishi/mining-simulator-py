from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class SimulationNode(ABC):
    """Base class for a simulation node in our system"""

    def __init__(self, idx: int, node_type: str):
        """Constructor for base simulation node class"""
        logger.debug("Initializing base class")
        self.idx = idx
        """Idenitifier for particular simulation node"""
        self.node_type = node_type
        """Simulation Node Type """
        self.current_tick = 0
        """Track the current clock tick from the simulation"""
        self._state = None
        """Represents state of the simulation node"""
        self._data_log_list = []
        """Log data list for Node Class"""

    def __str__(self):
        return f"{self.node_type}-ID-{self.idx}"

    @abstractmethod
    def _next_state(self):
        """Abstract method for evaluating next state of simulation node"""
        pass

    def get_state(self):
        """Returns the current state of the simulation node"""
        return self._state

    @abstractmethod
    def log_data(self):
        """Abstract method for data logging"""
        pass

    @abstractmethod
    def tick(self):
        """Abstract method for moving simulation node by one tick"""
        pass
