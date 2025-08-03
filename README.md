
# AI Data Center Energy Model (OpenStudio)

## Overview
This repository contains an OpenStudio model of a **500 MW hyperscale AI data center** located in **Abu Dhabi** simulating the hot climate areas. The model focuses on:
- Direct-to-Chip (D2C) liquid cooling
- Minimal lighting/occupancy loads
- Dedicated Outdoor Air System (DOAS) with dehumidification
- Water use and heat recovery estimation

The goal is to evaluate **energy performance**, **cooling strategies**, and **water consumption** in extreme climates.

---

## Repository Structure
- **`model/`** – Main OpenStudio files (`.osm`), weather data, and measures
- **`results/`** – Processed outputs, plots, and reports
- **`scripts/`** – Python scripts to extract and visualize results
- **`docs/`** – Methodology, schematics, and references
- **`README.md`** – You are here


## How to Run the Model and Generate Results

### 1. Requirements
- [OpenStudio](https://openstudio.net/) (tested on version X.X)
- Python 3.10+ with the following libraries:
  ```bash
  pip install pandas matplotlib

### 2. Run the OpenStudio Simulation
1. Open `model/base_model.osm` in OpenStudio.
2. Ensure the Abu Dhabi weather file (`model/AbuDhabi.epw`) is linked.
3. Run the simulation (this will generate `eplusout.sql` in `model/run/`).

### 3. Extract Results and generate plots
1. From the project root, run:
   ```bash
   python scripts/extract_and_plot.py



---

## How to Reproduce
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/AI-DataCenter-OpenStudio.git
