# Mining Simulator
The goal of this project is to develop a simulation for a space mining operation. This
simulation will manage and track the efficiency of mining trucks and unload stations over a
continuous 72-hour operation.

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Tested on Windows](https://img.shields.io/badge/Tested_on-Windows-brightgreen.svg)](https://www.microsoft.com/en-us/windows/)
[![Tested on Ubuntu](https://img.shields.io/badge/Tested_on-Ubuntu-orange.svg)](https://ubuntu.com/)

## Project Design and Sample Results
**Project Design and sample result files are available at:**

- `./docs/design.md`  -> System architecture documentation
- `./docs/sample_results.md` -> Sample results documentation

## Getting Started
NOTE: The MiningSimulator python scripts was developed 
1. Create virtual enviroment and activate it. 
```sh
python -m venv .venv
# For Windows based systems
.\.venv\Scripts\activate
```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the simulation:
   ```sh
   python run_simulation.py
   ```
   At the end of simulation, results are saved to:
   - Station stats are saved to `./results/station_stats.json`
   - Truck stats are saved to `./results/truck_stats.json`

 ### Unit Tests
 Run unit tests (if needed):
   ```sh
   pytest tests/
   ```


## Python Project Information
- Mining Simulator is developed using Python 3.12.7
- Flake8 is used for linting and Black is used for formatting.
- Pytest is used for unit and integration tests. 
- Project structure:
```
mining-simulator/
│-- mining_sim/         # Core simulation logic and components
│   │-- nodes/          # Data nodes for simulation
│   │-- enums/          # Enum values used for simulation
|   |-- utility/        # Utility and analysis scripts used for simulation
│   │-- __init__.py     # Module initialization
│
│-- tests/              # Unit and integration tests
│   │-- test_truck.py   # Unit Tests for MiningTruck nodes
│   │-- test_unloadstation.py  # Tests for UnloadStation nodes
|   |-- test_simulator.py # Unit Tests for MiningSimulator
|   |-- test_utility_functions.py # Unit Tests for utility functions
│
│-- docs/               # Documentation and guides
|   │-- design.md       # System architecture documentation
│   │-- sample_results.md # Sample results from Simulation
|
│-- run_simulation.py   # Script to run the simulation
│-- conftest.py         # Pytest conftest file
│-- .flake8             # Flake8 linting configuration
|-- requirements.txt    # Python (pip) requirements file
│-- pyproject.toml      # Project dependencies and configurations
│-- README.md           # Project overview and setup instructions
```






