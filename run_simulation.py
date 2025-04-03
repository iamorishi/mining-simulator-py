import logging

from mining_sim import MiningSimulator

logger = logging.getLogger(__name__)

# Setup simulator - NOTE: stop_time is in hours
sim = MiningSimulator(n_trucks=500, m_stations=20, stop_time_hr=72)

# Run the simulation
sim.run()

# Analyze the simulation logs
sim.analyze_simulation_logs()
