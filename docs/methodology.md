# Methodology

## 1. Objective
The purpose of this project is to model the energy, cooling, and water performance of a hyperscale AI data center in Abu Dhabi using OpenStudio and EnergyPlus. The model focuses on:
- Direct-to-Chip (D2C) liquid cooling
- Minimal lighting and occupancy loads
- Dedicated Outdoor Air System (DOAS) with dehumidification
- Water use and heat recovery estimation

---

## 2. Model Setup
### 2.1 Geometry and Zoning
- Single data center building divided into 100 zones (representing 100 aisles).
- Each aisle includes 60 high-performance compute racks with 8 DGX H100 systems per rack.

### 2.2 Internal Loads
- IT load: **81.6 kW per rack**, scaled to a **500 MW** facility.
- Minimal lighting and occupancy to reflect typical AI data center operation.

### 2.3 HVAC and Cooling
- Direct-to-Chip cooling approximated using a **chilled water loop**.
- Four-Pipe system used to represent cooling distribution, with minimising the fans power very much to reflect on the D2C system.
- Dedicated Outdoor Air System (DOAS) for dehumidification and ventilation.

---

## 3. Simulation and Outputs
- Simulations run in OpenStudio with Abu Dhabi EPW weather file.
- Key metrics extracted:
  - **Annual Energy Use Intensity (EUI)**
  - **Peak Cooling Load**
  - **Annual Water Use**
  - **Monthly and hourly load profiles**

Processed outputs and plots are available in the [`results/`](../results/) folder.

---

## 4. Reproducibility
1. Open `model/base_model.osm` in OpenStudio.
2. Run the simulation.
3. Review outputs in `results/`.

---

## 5. Future Work
- Expansion to 1 GW scale.
- Integration of battery storage and renewable energy scenarios.
- Refinement of D2C cooling parameters.
