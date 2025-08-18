import os, sqlite3, argparse, datetime as dt
import pandas as pd
import matplotlib.pyplot as plt

# ---- Config ----
DEFAULT_SQL = os.path.join("model", "run", "eplusout.sql")
OUT_DIR = os.path.join("results")
os.makedirs(OUT_DIR, exist_ok=True)

METER_CANDIDATES = {
    "facility_elec": [
        "Electricity:Facility", "ElectricityNet:Facility"
    ],
    "hvac_elec": [
        "Electricity:HVAC"
    ],
    "interior_equip": [
        "Electricity:InteriorEquipment"
    ],
    "ite_elec": [
        # If you used ITE objects with subcategory/meter reporting:
        "ITE:Electricity", "Electricity:ITE", "ITE Equipment Electricity"
    ],
    "cooling_elec": [
        "Cooling:Electricity"
    ],
    "mains_water": [
        "WaterSystems:MainsWater", "MainsWater:Facility"
    ]
}

def open_db(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Could not find EnergyPlus SQL at: {path}")
    return sqlite3.connect(path)

def get_env_info(conn):
    q = """SELECT Value FROM EnvironmentPeriods WHERE EnvironmentType = 'WeatherRunPeriod' LIMIT 1;"""
    try:
        row = conn.execute(q).fetchone()
        return row[0] if row else "RunPeriod"
    except sqlite3.Error:
        return "RunPeriod"

def meter_dict(conn):
    d = {}
    for name, alts in METER_CANDIDATES.items():
        meter_id = None
        for label in alts:
            row = conn.execute(
                "SELECT ReportMeterDataDictionaryIndex FROM ReportMeterDataDictionary WHERE MeterName = ? COLLATE NOCASE",
                (label,)
            ).fetchone()
            if row:
                meter_id = row[0]
                d[name] = (label, meter_id)
                break
        # silently skip if not found
    return d

def read_meter_timeseries(conn, meter_id):
    # Join to Time to build timestamps
    q = """
    SELECT
        Time.Year, Time.Month, Time.DayOfMonth, Time.Hour, Time.Minute, ReportMeterData.Value
    FROM ReportMeterData
    JOIN Time ON ReportMeterData.TimeIndex = Time.TimeIndex
    WHERE ReportMeterData.ReportMeterDataDictionaryIndex = ?
    ORDER BY Time.Year, Time.Month, Time.DayOfMonth, Time.Hour, Time.Minute
    """
    df = pd.read_sql_query(q, conn, params=(meter_id,))
    if df.empty:
        return df
    # EnergyPlus timestamps are at the *end* of the interval; construct pandas datetime
    df["timestamp"] = pd.to_datetime(dict(year=df.Year, month=df.Month, day=df.DayOfMonth, hour=df.Hour, minute=df.Minute))
    df = df[["timestamp", "Value"]].rename(columns={"Value": "value"})
    df = df.set_index("timestamp").sort_index()
    return df

def find_first_available(meter_map, key):
    return meter_map.get(key, (None, None))

def safe_plot(series, title, fname, ylabel="Rate (W or kg/s)"):
    if series is None or series.empty:
        print(f"[skip] No data for {title}")
        return
    plt.figure()
    series.plot()
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("Time")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, fname)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"[ok] Saved {path}")

def main(sql_path):
    conn = open_db(sql_path)
    env = get_env_info(conn)
    meters = meter_dict(conn)

    # Read available meters
    data = {}
    for key, (label, mid) in meters.items():
        df = read_meter_timeseries(conn, mid)
        data[key] = df.rename(columns={"value": key}) if not df.empty else pd.DataFrame()

    # Merge all to a single dataframe on timestamp
    dfs = [df for df in data.values() if not df.empty]
    if dfs:
        merged = pd.concat(dfs, axis=1)
        merged = merged.resample("1H").mean()  # standardize to hourly if needed
        csv_path = os.path.join(OUT_DIR, "timeseries_merged_hourly.csv")
        merged.to_csv(csv_path, index=True)
        print(f"[ok] Wrote {csv_path}")
    else:
        merged = pd.DataFrame()
        print("[warn] No meter data merged.")

    # Compute PUE if possible: Facility / IT
    pue_series = None
    if "facility_elec" in data and not data["facility_elec"].empty:
        if "ite_elec" in data and not data["ite_elec"].empty:
            aligned = data["facility_elec"].join(data["ite_elec"], how="inner")
            # Avoid divide-by-zero
            pue_series = (aligned["facility_elec"] / aligned["ite_elec"].replace(0, pd.NA)).dropna()
            pue_series = pue_series.resample("1H").mean()
        else:
            print("[info] IT electricity meter not found — PUE not computed (add ITE meters in the model).")

    # Plots
    safe_plot(
        data["facility_elec"].resample("1D").sum() if "facility_elec" in data and not data["facility_elec"].empty else None,
        f"Daily Facility Electricity — {env}",
        "daily_facility_electricity.png",
        ylabel="kWh/day (if hourly W, ensure conversion)"
    )
    safe_plot(
        data["hvac_elec"].resample("1D").sum() if "hvac_elec" in data and not data["hvac_elec"].empty else None,
        f"Daily HVAC Electricity — {env}",
        "daily_hvac_electricity.png"
    )
    safe_plot(
        data["mains_water"].resample("1D").sum() if "mains_water" in data and not data["mains_water"].empty else None,
        f"Daily Mains Water Use — {env}",
        "daily_mains_water.png",
        ylabel="m³/day (check meter units)"
    )
    if pue_series is not None and not pue_series.empty:
        safe_plot(
            pue_series,
            f"PUE (Hourly) — {env}",
            "pue_hourly.png",
            ylabel="PUE"
        )

    # Simple kpis
    if not merged.empty:
        kpi = {}
        if "facility_elec" in merged:
            kpi["Facility kWh (sum)"] = merged["facility_elec"].sum() / 1000.0  # adjust if units already kWh
        if "hvac_elec" in merged:
            kpi["HVAC kWh (sum)"] = merged["hvac_elec"].sum() / 1000.0
        if "mains_water" in merged:
            kpi["Mains Water (sum)"] = merged["mains_water"].sum()
        if pue_series is not None and not pue_series.empty:
            kpi["PUE (mean)"] = float(pue_series.mean())
        kpi_df = pd.DataFrame.from_dict(kpi, orient="index", columns=["value"])
        kpi_csv = os.path.join(OUT_DIR, "kpis.csv")
        kpi_df.to_csv(kpi_csv)
        print(f"[ok] Wrote {kpi_csv}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sql", default=DEFAULT_SQL, help="Path to EnergyPlus eplusout.sql")
    args = ap.parse_args()
    main(args.sql)
