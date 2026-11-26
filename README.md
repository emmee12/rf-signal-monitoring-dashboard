# RF Signal Monitoring & Diagnostics Dashboard

An end-to-end Radio Frequency (RF) telemetry processing pipeline and interactive diagnostic dashboard modeled after emergency public-safety P25 radio field-testing workflows.

## Pipeline Architecture
1. **Telemetry Ingestion & Generation (`generate_rf_logs.py`):** Simulates multi-facility emergency radio field readings (`RSSI` in dBm, `SINR` in dB, `DAQ` audio scores, and `700/800 MHz` frequencies).
2. **ETL Standardization (`rf_etl_pipeline.py`):** Cleans raw CSV exports, strips unit strings, enforces data types, and evaluates public-safety compliance thresholds (`RSSI >= -95.0 dBm` and `DAQ >= 3.0`).
3. **Cloud Query Layer (`athena_queries.sql`):** External table DDL and analytical SQL queries designed for AWS S3, AWS Glue Crawlers, and Amazon Athena dead-zone isolation.
4. **Interactive Diagnostics UI (`dashboard.html`):** Zero-dependency Chart.js dashboard allowing engineers and facility stakeholders to filter by building and pinpoint zones requiring Bi-Directional Amplifier (BDA) remediation.

## Quick Start
```bash
pip install pandas
python generate_rf_logs.py
python rf_etl_pipeline.py