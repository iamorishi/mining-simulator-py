import os
import logging
import pandas as pd
import json

from mining_sim.nodes.truck import MiningTruck
from mining_sim.nodes.unloadstation import UnloadingStation

logger = logging.getLogger(__name__)


# NOTE: Due to lack of time, no unit tests have been written for these functions
def make_results_dir():
    """Create a results directory if it does not exist"""
    results_dir = "./results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)


def convert_log_to_df(nodes: list[MiningTruck | UnloadingStation]) -> pd.DataFrame:
    """Convert log data to list of pandas dataframe

    Args:
        nodes: List of nodes whose log data needs to be converted
    """
    df_list = []
    for node in nodes:
        df_list.append(pd.DataFrame(node._data_log_list))

    return df_list


def process_truck(truck_df: pd.DataFrame) -> pd.DataFrame:
    # Initialize required counters and columns in DataFrame
    time_mining, time_onroad, time_unloading, time_queued = 0, 0, 0, 0
    mining_trips, unloads, roundtrips = 0, 0, 0
    truck_df = truck_df.sort_values(["tick"]).copy()
    truck_df["Time_Mining"] = 0
    truck_df["Time_OnRoad"] = 0
    truck_df["Time_Unloading"] = 0
    truck_df["Time_Queued"] = 0
    truck_df["Mining_Trips_Completed"] = 0
    truck_df["Unloads_Completed"] = 0
    truck_df["Roundtrips_Completed"] = 0
    # Iterate over rows to compute values
    prev_state = "None"
    for i, row in truck_df.iterrows():
        # Time spent in each state
        if row["state"] == "AtMine":
            time_mining += 1
        elif "OnRoad" in row["state"]:
            time_onroad += 1
        elif row["state"] == "Unloading":
            if prev_state == "Unloading":
                time_queued += 1
            else:
                time_unloading += 1

        # Detect state transitions
        if prev_state == "AtMine" and "OnRoad" in row["state"]:
            mining_trips += 1
        elif prev_state == "Unloading" and "OnRoad" in row["state"]:
            unloads += 1
        elif "OnRoad" in prev_state and row["state"] == "AtMine":
            roundtrips += 1

        prev_state = row["state"]

        # Update cumulative values in DataFrame
        truck_df.at[i, "Time_Mining"] = time_mining
        truck_df.at[i, "Time_OnRoad"] = time_onroad
        truck_df.at[i, "Time_Unloading"] = time_unloading
        truck_df.at[i, "Time_Queued"] = time_queued
        truck_df.at[i, "Mining_Trips_Completed"] = mining_trips
        truck_df.at[i, "Unloads_Completed"] = unloads
        truck_df.at[i, "Roundtrips_Completed"] = roundtrips

    return truck_df


def compute_truck_metrics(df_list=list[pd.DataFrame]):
    """Compute truck metrics based on input dataframe"""
    # Sort by tick within each truck ID
    analyzed_df_list = []
    for df in df_list:
        analyzed_df_list.append(process_truck(df))

    return analyzed_df_list


def compute_cumulative_truck_stats(df_list, output_file="./results/truck_stats.json"):
    """
    Compute cumulative time statistics for each truck at the last tick
    and save the result as a JSON file.
    """
    # Grab the last row for each truck's dataframe and create new dataframe
    last_tick_rows = []
    for df in df_list:
        last_tick_rows.append(df.loc[df["tick"].idxmax()])

    # Convert the list of rows into a new DataFrame
    last_tick_df = pd.DataFrame(last_tick_rows)

    # Calculate total time per truck
    last_tick_df["Total_Time"] = (
        last_tick_df["Time_Mining"]
        + last_tick_df["Time_OnRoad"]
        + last_tick_df["Time_Unloading"]
        + last_tick_df["Time_Queued"]
    )

    # Compute percentages and efficiency (any time spent in queueing = not efficient)
    last_tick_df["Mining_pct"] = (last_tick_df["Time_Mining"] / last_tick_df["Total_Time"]) * 100
    last_tick_df["OnRoad_pct"] = (last_tick_df["Time_OnRoad"] / last_tick_df["Total_Time"]) * 100
    last_tick_df["Unloading_pct"] = (last_tick_df["Time_Unloading"] / last_tick_df["Total_Time"]) * 100
    last_tick_df["Queued_pct"] = (last_tick_df["Time_Queued"] / last_tick_df["Total_Time"]) * 100
    last_tick_df["Efficiency_pct"] = (
        (last_tick_df["Total_Time"] - last_tick_df["Time_Queued"]) / last_tick_df["Total_Time"]
    ) * 100

    # Select relevant columns
    stats_df = last_tick_df[
        [
            "id",
            "Mining_pct",
            "OnRoad_pct",
            "Unloading_pct",
            "Queued_pct",
            "Efficiency_pct",
            "Time_Unloading",
            "Total_Time",
        ]
    ]

    # Convert to dictionary and save as JSON
    stats_dict = stats_df.set_index("id").to_dict(orient="index")
    make_results_dir()
    with open(output_file, "w") as f:
        json.dump(stats_dict, f, indent=4)

    print(f"Stats saved to {output_file}")
    avg_stats = stats_df.mean().to_dict()

    # Print average stats across trucks
    print("\n### Average Stats Across All Trucks ###")
    for key, value in avg_stats.items():
        if key == "Time_Unloading":
            print(f"Helium Unloads: {value}")
        elif key not in ["Total_Time", "id"]:
            print(f"{key}: {value:.2f}%")

    return stats_dict


def compute_station_metrics(df_list: list[pd.DataFrame], output_file: str = "./results/station_stats.json"):
    results_dict = []

    for df in df_list:
        # Initialize variables to store aggregated metrics
        total_time = 0
        total_wait_time = 0

        # Count the total number of ticks
        total_time += df["tick"].nunique()

        # Calculate the number of instances where wait_time > 2 for each tick
        time_queued = (df["wait_time"] > 2).sum()

        # Calculate the average wait time, max wait time, efficiency percentage
        total_wait_time += df["wait_time"].sum()
        max_wait_time = df["wait_time"].max()
        average_wait_time = total_wait_time / total_time
        efficiency_pct = (1 - (time_queued / total_time)) * 100

        result_dict = {
            "station_id": int(df["id"].iloc[0]),
            "average_wait_time": float(average_wait_time),
            "max_wait_time": float(max_wait_time),
            "efficiency_pct": float(efficiency_pct),
        }
        results_dict.append(result_dict)

    # Save the results to a JSON file
    make_results_dir()
    with open(output_file, "w") as f:
        json.dump(results_dict, f, indent=4)
        print(f"Stats saved to {output_file}")

    # Print the average stats across all stations
    print("\n### Average Stats Across All Stations###")
    avg_wait_time = sum([x["average_wait_time"] for x in results_dict]) / len(results_dict)
    avg_max_wait_time = sum([x["max_wait_time"] for x in results_dict]) / len(results_dict)
    avg_efficiency_pct = sum([x["efficiency_pct"] for x in results_dict]) / len(results_dict)
    print(f"Average Wait Time: {avg_wait_time:.2f} ticks")
    print(f"Average Max Wait Time: {avg_max_wait_time:.2f} ticks")
    print(f"Average Efficiency Percentage: {avg_efficiency_pct:.2f}%")
