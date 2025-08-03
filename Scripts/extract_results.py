import sqlite3
import pandas as pd
import os

# Path to the SQL output (update as needed)
sql_path = os.path.join("model", "run", "eplusout.sql")

if not os.path.exists(sql_path):
    raise FileNotFoundError(f"SQL file not found at {sql_path}. Run the OpenStudio simulation first.")

# Connect to the EnergyPlus SQL database
conn = sqlite3.connect(sql_path)

# Example 1: Get annual site energy use (kWh)
query_total_energy = """
SELECT Value 
FROM TabularDataWithStrings 
WHERE ReportName='AnnualBuildingUtilityPerformanceSummary'
AND TableName='Site and Source Energy'
AND ColumnName='Total Site Energy'
"""
total_energy = conn.execute(query_total_energy).fetchone()
print(f"Total Site Energy (GJ): {total_energy[0]}")

# Example 2: Get annual water use (m³)
query_water = """
SELECT Value 
FROM TabularDataWithStrings 
WHERE ReportName='AnnualBuildingUtilityPerformanceSummary'
AND TableName='Water End Uses'
AND ColumnName='Total Water'
"""
water_use = conn.execute(query_water).fetchone()
print(f"Total Water Use (m³): {water_use[0]}")

# Example 3: Export monthly cooling loads
query_cooling = """
SELECT RowName, Value 
FROM TabularDataWithStrings
WHERE ReportName='EnergyMeters'
AND TableName='Annual and Monthly Values'
AND ColumnName='Cooling:Electricity [kWh]'
"""
cooling_data = conn.execute(query_cooling).fetchall()
cooling_df = pd.DataFrame(cooling_data, columns=["Month", "Cooling_kWh"])
cooling_df.to_csv(os.path.join("results", "monthly_cooling.csv"), index=False)
print("Monthly cooling loads saved to results/monthly_cooling.csv")

conn.close()
