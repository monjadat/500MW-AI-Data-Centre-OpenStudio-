import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# Paths
sql_path = os.path.join("model", "run", "eplusout.sql")
results_folder = "results"
os.makedirs(results_folder, exist_ok=True)

if not os.path.exists(sql_path):
    raise FileNotFoundError(f"SQL file not found at {sql_path}. Run the OpenStudio simulation first.")

# --- Extract from SQL ---
conn = sqlite3.connect(sql_path)

# Total Site Energy (GJ)
query_total_energy = """
SELECT Value 
FROM TabularDataWithStrings 
WHERE ReportName='AnnualBuildingUtilityPerformanceSummary'
AND TableName='Site and Source Energy'
AND ColumnName='Total Site Energy'
"""
total_energy = conn.execute(query_total_energy).fetchone()
print(f"Total Site Energy (GJ): {total_energy[0]}")

# Total Water Use (m³)
query_water = """
SELECT Value 
FROM TabularDataWithStrings 
WHERE ReportName='AnnualBuildingUtilityPerformanceSummary'
AND TableName='Water End Uses'
AND ColumnName='Total Water'
"""
water_use = conn.execute(query_water).fetchone()
print(f"Total Water Use (m³): {water_use[0]}")

# Monthly Cooling (kWh)
query_cooling = """
SELECT RowName, Value 
FROM TabularDataWithStrings
WHERE ReportName='EnergyMeters'
AND TableName='Annual and Monthly Values'
AND ColumnName='Cooling:Electricity [kWh]'
"""
cooling_data = conn.execute(query_cooling).fetchall()
conn.close()

cooling_df = pd.DataFrame(cooling_data, columns=["Month", "Cooling_kWh"])
cooling_csv_path = os.path.join(results_folder, "monthly_cooling.csv")
cooling_df.to_csv(cooling_csv_path, index=False)
print(f"Monthly cooling loads saved to {cooling_csv_path}")

# --- Generate Plot ---
month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
cooling_df["Month"] = pd.Categorical(cooling_df["Month"], categories=month_order, ordered=True)
cooling_df = cooling_df.sort_values("Month")

plt.figure(figsize=(10, 6))
plt.bar(cooling_df["Month"], cooling_df["Cooling_kWh"], color="steelblue")
plt.xlabel("Month")
plt.ylabel("Cooling Load (kWh)")
plt.title("Monthly Cooling Loads")
plt.xticks(rotation=45)
plt.tight_layout()

plot_path = os.path.join(results_folder, "monthly_cooling_plot.png")
plt.savefig(plot_path, dpi=300)
print(f"Plot saved to {plot_path}")
