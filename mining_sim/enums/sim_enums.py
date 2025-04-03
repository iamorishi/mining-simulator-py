from enum import Enum


class TruckState(Enum):
    """Enum defining the state(position) of a mining truck"""

    OnRoad_ToMine = 0
    """Indicates mining truck is on the road to the mine"""
    AtMine = 1
    """Indicates mining truck is currently at the mining site"""
    OnRoad_ToUnload = 2
    """Indicates that the mining truck is on the road to the unload station"""
    Unloading = 3
    """Indicates mining truck is actively unloading the mined helium"""


class UnloadStationState(Enum):
    """Enum defining the state of the unloading station"""

    Unoccupied = 0
    """Indicates that the unloading station is unoccupied"""
    Occupied = 1
    """Indicates that the unloading station is occupied"""
