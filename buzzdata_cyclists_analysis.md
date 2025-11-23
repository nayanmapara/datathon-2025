# BuzzData Cyclists Analysis – Risk Map & Safe Path

This document describes the analysis performed on  
`BuzzData_cyclists_toronto_1986-2010.csv` as part of the **SafeRoute AI / Crime_WalkSafe** project.

The goal is to use historical cyclist collision data in Toronto to:

1. Build a **spatial risk map** showing which areas are more dangerous for cyclists.
2. Compute a **cyclist collision risk score** for each grid cell in the city.
3. Use that risk information to support **safe path recommendation** (safest route vs. shortest route).

---

## 1. Dataset Used

### File
`BuzzData_cyclists_toronto_1986-2010.csv`

### Key Columns Used

- `INJURY` – injury severity for the cyclist  
- `SAFETY EQUIP.` – safety equipment used (e.g., helmet)  
- `ROAD CLASS` – road type (Local, Collector, Minor/Major Arterial, Expressway)  
- `CYCLIST CRASH TYPE` – mechanism of crash (Dooring, Left Turn, etc.)  
- `AGE` – cyclist’s age  
- `STNAME1`, `STREET 1 TYPE` – primary street name and type  
- `STNAME 2`, `STREET 2 TYPE` – cross street and type  
- `LONG`, `LAT` – longitude and latitude of collision  
- `ACC TIME` – timestamp of collision  
- `TRAFFIC CONTROL` – type of control (signal, stop sign, etc.)  
- `ROAD SURFACE` – surface condition (Dry, Wet, Snow, Ice)  
- `DATE`, `DATE.year`, `DATE.month`, `DATE.day-of-month`, `DATE.day-of-week`  
- `ACC TIME.hour`, `ACC TIME.minute` – derived time fields  

Only these columns are required for the cyclist‑risk analysis.

---

## 2. Analysis Pipeline Overview

The script `buzzdata_cyclists_analysis.py` follows this pipeline:

1. **Load & Clean Data**
   - Read the CSV.
   - Drop records with missing `LAT` or `LONG`.

2. **Spatial Grid Mapping**
   - Convert `LAT` and `LONG` into a **10 × 10 grid**:
     - `lat_bin` ∈ [0, 9]
     - `lon_bin` ∈ [0, 9]
   - Create a `cell_id` = `"lat_bin_lon_bin"` for each collision.

3. **Risk Scoring per Collision**
   - Create several component scores:
     - **Injury score** from `INJURY`
     - **Road class score** from `ROAD CLASS`
     - **Crash type score** from `CYCLIST CRASH TYPE`
     - **Time-of-day score** from `ACC TIME.hour`
     - **Surface score** from `ROAD SURFACE`
   - Combine them into a single `collision_risk` value for each collision.

4. **Risk Aggregation per Cell**
   - Group by `cell_id`.
   - Sum all `collision_risk` values within the cell → `cyclist_risk`.
   - Normalize `cyclist_risk` to a 0–100 **risk_score** for visualization.

5. **Grid Graph Construction**
   - Build a `networkx` **grid graph**, where:
     - Nodes = `(lat_bin, lon_bin)` cells.
     - Each node stores a `risk` attribute from `risk_score`.

6. **Safest Path Computation**
   - Define an edge weight:
     \[
     \text{weight} = 1 \times (1 + \text{avg\_risk}_{u,v})
     \]
     where `avg_risk` is the mean risk of the two endpoint nodes.
   - Run **Dijkstra’s algorithm** to find the **lowest‑risk path** between:
     - `START_CELL = (0, 0)`
     - `END_CELL = (N_LAT_BINS - 1, N_LON_BINS - 1)` (bottom‑right corner).
   - This represents the **safest route through the grid**, based only on cyclist risk.

7. **Visualization**
   - Create a **heatmap** of `risk_score` over the grid.
   - Overlay the **safest path** in blue on top of the heatmap.

---

## 3. Risk Scoring Details

Each collision’s risk is computed as:

```text
collision_risk =
    1.5 * injury_score
  + 1.2 * road_score
  + 1.3 * crash_score
  + 1.1 * time_score
  + 1.0 * surface_score
