import os
import pandas as pd

def run_rf_etl(input_csv="raw_rf_field_logs.csv", output_dir="processed"):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(input_csv)

    # 1. Clean whitespace and strip unit suffixes ('dBm')
    df["facility_name"] = df["facility_name"].str.strip()
    df["rssi_dbm"] = (
        df["rssi_dbm"]
        .astype(str)
        .str.replace("dBm", "", regex=False)
        .str.strip()
        .astype(float)
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["test_date"] = df["timestamp"].dt.date

    # 2. Classify Public Safety Radio Compliance (Threshold: RSSI >= -95 dBm & DAQ >= 3.0)
    def classify_signal(row):
        if row["rssi_dbm"] < -95.0 or row["daq_score"] < 3.0:
            return "CRITICAL_FAIL"
        elif row["rssi_dbm"] < -88.0 or row["daq_score"] < 3.4:
            return "MARGINAL_WARNING"
        return "COMPLIANT_PASS"

    df["compliance_status"] = df.apply(classify_signal, axis=1)

    # 3. Export clean fact table for AWS S3 / Athena ingestion
    clean_path = os.path.join(output_dir, "rf_telemetry_clean.csv")
    df.to_csv(clean_path, index=False)

    # 4. Build aggregated facility & zone summary for executive dashboarding
    summary = (
        df.groupby(["facility_name", "facility_type", "municipality", "building_zone"], as_index=False)
        .agg(
            total_tests=("test_id", "count"),
            avg_rssi_dbm=("rssi_dbm", "mean"),
            avg_sinr_db=("sinr_db", "mean"),
            avg_daq_score=("daq_score", "mean"),
            critical_fails=("compliance_status", lambda s: (s == "CRITICAL_FAIL").sum()),
        )
    )
    summary["avg_rssi_dbm"] = summary["avg_rssi_dbm"].round(2)
    summary["avg_sinr_db"] = summary["avg_sinr_db"].round(2)
    summary["avg_daq_score"] = summary["avg_daq_score"].round(2)
    summary["pass_rate_pct"] = (
        ((summary["total_tests"] - summary["critical_fails"]) / summary["total_tests"]) * 100
    ).round(1)

    summary_path = os.path.join(output_dir, "facility_zone_diagnostics.csv")
    summary.to_csv(summary_path, index=False)
    print(f"ETL Complete: Saved {clean_path} and {summary_path}")

if __name__ == "__main__":
    run_rf_etl()