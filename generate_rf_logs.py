import random
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)

FACILITIES = [
    ("Montgomery County High School A", "Educational", "Silver Spring, MD"),
    ("Prince George's Municipal Center", "Government", "Upper Marlboro, MD"),
    ("Howard County General Wing B", "Healthcare", "Columbia, MD"),
    ("Anne Arundel Transit Hub", "Transportation", "Annapolis, MD"),
    ("Bethesda Metro Underground Concourse", "Subterranean", "Bethesda, MD"),
    ("College Park Campus Arena", "Educational", "College Park, MD"),
]

ZONES = ["Lobby / Ground Floor", "Basement / Mechanical", "Stairwell North", "2nd Floor Corridor", "Elevator Core"]
FREQUENCIES_MHZ = [771.18125, 772.43125, 854.96250, 856.21250]

def generate_telemetry(num_records=5000):
    rows = []
    base_time = datetime(2026, 4, 1, 8, 0, 0)

    for i in range(1, num_records + 1):
        facility, f_type, city = random.choice(FACILITIES)
        zone = random.choice(ZONES)
        freq = random.choice(FREQUENCIES_MHZ)
        timestamp = (base_time + timedelta(minutes=i * 3)).strftime("%Y-%m-%d %H:%M:%S")

        # Simulate realistic RF attenuation in basements, stairwells, and subterranean structures
        penalty = 0
        if "Basement" in zone or "Elevator" in zone or f_type == "Subterranean":
            penalty = random.uniform(14.0, 24.0)
        elif "Stairwell" in zone:
            penalty = random.uniform(8.0, 15.0)

        rssi = round(random.uniform(-84.0, -68.0) - penalty, 1)
        sinr = round(random.uniform(16.0, 26.0) - (penalty * 0.55), 1)

        # Map signal strength to Digital Audio Quality (DAQ 1.0 - 5.0)
        if rssi >= -85 and sinr >= 15:
            daq = round(random.uniform(3.8, 4.8), 1)
        elif rssi >= -95 and sinr >= 10:
            daq = round(random.uniform(3.0, 3.7), 1)
        else:
            daq = round(random.uniform(1.8, 2.9), 1)

        # Inject occasional messy formatting to demonstrate ETL cleaning
        rssi_str = f"{rssi} dBm" if i % 15 == 0 else str(rssi)
        rows.append({
            "test_id": f"RF-{i:05d}",
            "timestamp": timestamp,
            "facility_name": f"  {facility} " if i % 20 == 0 else facility,
            "facility_type": f_type,
            "municipality": city,
            "building_zone": zone,
            "frequency_mhz": freq,
            "rssi_dbm": rssi_str,
            "sinr_db": sinr,
            "daq_score": daq
        })

    df = pd.DataFrame(rows)
    df.to_csv("raw_rf_field_logs.csv", index=False)
    print(f"Generated {len(df)} raw RF field-test records -> raw_rf_field_logs.csv")

if __name__ == "__main__":
    generate_telemetry(5000)