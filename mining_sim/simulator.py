"""Mining Simulator for helium miners on the moon"""

import bisect
import logging
import sys
import time
from datetime import datetime
import random

from mining_sim.nodes.truck import MiningTruck
from mining_sim.nodes.unloadstation import UnloadingStation
from mining_sim.enums.sim_enums import TruckState
from mining_sim.utility.analysis import (
    convert_log_to_df,
    compute_truck_metrics,
    compute_cumulative_truck_stats,
    compute_station_metrics,
)

logger = logging.getLogger(__name__)

# Seed random here for reproducibility
random.seed(42)


def find_station_info_by_id(station_infos, station_id) -> dict | None:
    """Utility function to find station by id in station_infos

    Args:
        station_infos (list[dict]): List of station assignments dict
        station_id(int): Station ID to use for looking up staiton assignments dict

    Returns:
        dict: If found, station assignment dict for station_id else None
    """
    for station in station_infos:
        if station["station_id"] == station_id:
            return station
    return None  # Return None if no station with the given id is found


def get_truck_assignments(station_infos) -> list[dict]:
    """From a given station assignments file, return the corresponding truck assignments

    Args:
        station_infos (list[dict]): List of station assignments dict

    Returns:
        list[dict]: List of truck assignments dict
    """
    assignments = []
    for station in station_infos:
        # For each truck assigned to this station, add it to the assignments list
        for truck in station["q_trucks"]:
            assignments.append({"truck_id": truck, "station_id": station["station_id"]})
    return assignments


dots = ["   ", ".  ", ".. ", "..."]


def animate_output(ticks):
    """Animate the 'Running Simulation' terminal output"""
    sys.stdout.write(f"\rRunning Simulation{dots[ticks % len(dots)]} : T = {ticks*5/60} hours")
    sys.stdout.flush()
    time.sleep(0.005)


class MiningSimulator:
    """Class for creating a Mining Simulator"""

    def __init__(self, n_trucks: int, m_stations: int, stop_time_hr: int = 72, max_time_hr: int = 120):
        """Mining Simulation Constructor

        Args:
            n_trucks (int): Number of trucks in the simulation
            m_stations (int): Number of unloading stations in the simulation
            stop_time (hours): Simulation stop time in hours
            max_time (hours): Maximum runtime of simulation.
        """
        self.num_trucks = n_trucks
        """Number of trucks in the simulation"""
        self.num_stations = m_stations
        """Number of unloading stations in the simulation"""
        self.stop_time = int(stop_time_hr * 60 / 5)  # Convert hours to ticks ( 1 tick = 5 minutes)
        """Simulation stop time (in ticks)"""
        self.max_time = int(max_time_hr * 60 / 5)  # Convert hours to ticks ( 1 tick = 5 minutes)
        """Simulation stop time (in ticks)"""
        self.mining_trucks: list[MiningTruck] = []
        """List to hold mining trucks in the simulation"""
        self.unloading_stations: list[UnloadingStation] = []
        """List to hold unloading station in the simulation"""
        self.current_tick = 0
        """Tick counter of the simulation"""

        # Initialize Mining Trucks
        for idx in range(self.num_trucks):
            self.mining_trucks.append(MiningTruck(idx))

        for idx in range(self.num_stations):
            self.unloading_stations.append(UnloadingStation(idx))

    def assign_stations_algo(self, new_trucks: list[int], __station_infos: list[dict] = []):
        """Algorithm to assign mining trucks to station queue

        Args:
            new_trucks (list[int]): List of truck IDs to be assigned to queue
            __station_infos (list[dict]): Do not pass any values to this argument.
            This argument is only for unit testing purposes.

        Returns:
            station_infos (list[dict]): List of station infos dict with following
            truck_infos (list[dict]): List of truck assignments to station ID
        """
        if not __station_infos:
            station_infos = []
            for station in self.unloading_stations:
                # Populate station info
                station_infos.append(
                    {
                        "station_id": station.idx,
                        "wait_time": station.get_wait_time(),
                        "q_trucks": [],
                    }
                )
        else:
            station_infos = __station_infos

        logger.debug(f"Station infos initialized with {len(station_infos)} elems, new trucks {len(new_trucks)}")

        # ------------------------------------------------------------------------------------------------------#
        # ASIGNMENT ALGORITHM INFO
        # 1. Sort station info based on wait time and find min wait time
        # 2. Assign trucks to unloading station with shortest queue time
        # until all new trucks are exhausted in round robin fashion
        # ------------------------------------------------------------------------------------------------------#

        # Sort based on queue wait time in ascending order
        station_infos.sort(key=lambda x: x["wait_time"] + len(x["q_trucks"]))

        # Assign trucks to queue with lowest queue times in round robin fashion
        while new_trucks:
            # Get the lowest wait_time stations
            logger.debug(f"New Trucks:{new_trucks}")
            min_wait_time = station_infos[0]["wait_time"] + len(station_infos[0]["q_trucks"])
            logger.debug(f"Min Wait Time: {min_wait_time}")
            stations_with_min_wait = []

            while (
                station_infos and (station_infos[0]["wait_time"] + len(station_infos[0]["q_trucks"])) == min_wait_time
            ):
                stations_with_min_wait.append(station_infos.pop(0))

            logger.debug(f"Stations with min wait time: {len(stations_with_min_wait)}")
            # Assign multiple trucks to these stations
            for station in stations_with_min_wait:
                # Assign one truck at a time (or more if there are still trucks)
                if new_trucks:
                    station["q_trucks"].append(new_trucks.pop(0))
                else:
                    break

            # Re-insert stations with updated wait_time back into sorted list
            for station in stations_with_min_wait:
                bisect.insort(station_infos, station, key=lambda x: x["wait_time"] + len(x["q_trucks"]))

        station_infos.sort(key=lambda x: x["station_id"])
        if len(station_infos) != self.num_stations:
            logger.warning("Number of Station Assignments not equal to Num of Stations")

        truck_infos = get_truck_assignments(station_infos)
        return station_infos, truck_infos

    def tick(self):
        """Function to move the simulation forward by one tick"""
        # --------------------- SIMULATION TICK INFO -----------------------------------------------#
        # To move the simulation forward by one tick, the following needs to happen:
        # 1. Increment simulation tick counter (current_tick)
        # 2. Find trucks with = UnloadStation state AND not queued
        # 3. Pass these trucks to the assignment algo and get station assignments
        # 4. Move all other trucks (not in Unloading state) forward by one tick
        # 5. Move all unloading stations by one tick (passing in new truck assignments)
        # 6. Tick remaining trucks with Unloading State AND unload queued
        # --------------------- SIMULATION TICK INFO -----------------------------------------------#

        # 1. Increment simulation tick counter (current_tick)
        self.current_tick += 1

        # 2. Find trucks with = UnloadStation state AND not queued
        new_trucks = []  # List to hold new trucks ready to be queued/unloaded
        for truck in self.mining_trucks:
            if truck.get_state() == TruckState.Unloading and not truck.unload_queued:
                logger.debug(f"At T={self.current_tick}, added {truck} to assignment list")
                new_trucks.append(truck.idx)

        # 3. Pass these trucks to the assignment algo and get station assignments
        station_assignments = []
        truck_assignments = []
        if new_trucks:
            logger.debug(f"At T={self.current_tick}, {len(new_trucks)} trucks waiting for unload station")
            station_assignments, truck_assignments = self.assign_stations_algo(new_trucks)
        if new_trucks:
            logger.warning("New Trucks list is not empty. ALL TRUCKS NOT ASSIGNED!!")

        # 4. Move all other trucks (not in Unloading state) forward by one tick
        for truck in self.mining_trucks:
            if truck.get_state() != TruckState.Unloading:
                truck.tick()

        # 5. Move all unloading stations by one tick (passing in new truck assignments)
        _trucks_unload_complete = []  # Track the trucks that completed unloading
        for station in self.unloading_stations:
            station_assignment: dict = find_station_info_by_id(station_assignments, station_id=station.idx)
            if station_assignment is None:
                logger.debug(f"Station Assignment not found for: {station}, assignment skipped")
                _get_truck = station.tick(trucks=[])
            else:
                # Get truck that finished unloading (if any)
                _get_truck = station.tick(trucks=station_assignment["q_trucks"])

            if _get_truck is not None:
                _trucks_unload_complete.append(_get_truck)

        # 6. Tick remaining trucks with Unloading State AND unload queued
        # Based on truck assignments, first update each truck's unloading status
        for truck_assignment in truck_assignments:
            truck_idx = truck_assignment["truck_id"]
            if truck_idx != self.mining_trucks[truck_idx].idx:
                logger.error(f"truck_idx: {truck_idx} does not match expected {self.mining_trucks[truck_idx].idx}")
                logger.error(f"truck assignment: {truck_assignment}")
                raise ValueError("Truck indexes don't match")

            truck: MiningTruck = self.mining_trucks[truck_idx]
            truck.assign_unload_site(truck_assignment["station_id"])

        # Move other trucks still in unloading state
        # NOTE: This logic of updating ticks for different can be improved, but leave
        # as is for now due to time constraints.
        for truck in self.mining_trucks:
            if truck.get_state() == TruckState.Unloading and truck.unload_queued:
                _unload_complete = True if truck.idx in _trucks_unload_complete else False

                truck.tick(unloading_complete=_unload_complete)
                logger.debug(
                    f"Truck: {truck} , Tick Count: {truck.current_tick} , Truck State: {truck.get_state().name}"
                )

    def run(self):
        """Function to run the simulation until stop time passed through class constructor"""
        sim_stop_time = min(self.stop_time, self.max_time)
        print(f"\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Simulation started!")
        print(f"Num of Trucks: {self.num_trucks}, Num of Stations: {self.num_stations}")

        while self.current_tick <= sim_stop_time:
            if self.current_tick % 12 == 0:
                animate_output(self.current_tick)
            # Simulation tick
            self.tick()

        sys.stdout.flush()
        print(f"\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Simulation Complete! :)")

    def analyze_simulation_logs(self):
        """Function for analyzing data logs from the simulation"""

        # Convert log data to pandas data frame
        truck_df_list = convert_log_to_df(self.mining_trucks)
        station_df_list = convert_log_to_df(self.unloading_stations)

        # Compute metrics
        print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Analyzing Trucks Log Data (can take a few minutes)...")
        # NOTE: Analysis functions are not optimised for speed right now
        if len(self.mining_trucks) > 1000:
            print("WARNING: Large number of trucks input to simulation. Analysis will take a while!!!")

        # COmpute and output truck metrics
        truck_df_list = compute_truck_metrics(truck_df_list)
        compute_cumulative_truck_stats(truck_df_list)

        # Compute and output station metrics
        print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Analyzing Trucks Log Data (can take a few minutes)...")
        compute_station_metrics(station_df_list)

        # Exit
        print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Analysis Complete! :)")
