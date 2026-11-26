-- 1. Create External Table over AWS S3 Processed Telemetry Partition
CREATE EXTERNAL TABLE IF NOT EXISTS rf_diagnostics_db.rf_telemetry_clean (
    test_id STRING,
    timestamp TIMESTAMP,
    facility_name STRING,
    facility_type STRING,
    municipality STRING,
    building_zone STRING,
    frequency_mhz DOUBLE,
    rssi_dbm DOUBLE,
    sinr_db DOUBLE,
    daq_score DOUBLE,
    test_date DATE,
    compliance_status STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://emmee-rf-telemetry-prod/processed/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- 2. Isolate High-Risk Emergency Radio Dead Zones (< 85% Pass Rate)
SELECT 
    facility_name,
    building_zone,
    COUNT(*) AS total_readings,
    ROUND(AVG(rssi_dbm), 2) AS mean_rssi_dbm,
    ROUND(AVG(daq_score), 2) AS mean_daq,
    SUM(CASE WHEN compliance_status = 'CRITICAL_FAIL' THEN 1 ELSE 0 END) AS failed_tests,
    ROUND(
        100.0 * SUM(CASE WHEN compliance_status <> 'CRITICAL_FAIL' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS compliance_pass_rate_pct
FROM rf_diagnostics_db.rf_telemetry_clean
GROUP BY facility_name, building_zone
HAVING compliance_pass_rate_pct < 85.0
ORDER BY compliance_pass_rate_pct ASC;

-- 3. Frequency Band Attenuation Comparison (700 MHz vs. 800 MHz Public Safety Bands)
SELECT 
    CASE 
        WHEN frequency_mhz < 800 THEN '700 MHz Band'
        ELSE '800 MHz Band'
    END AS spectrum_band,
    COUNT(*) AS sample_count,
    ROUND(AVG(rssi_dbm), 2) AS avg_rssi_dbm,
    ROUND(AVG(sinr_db), 2) AS avg_sinr_db,
    ROUND(AVG(daq_score), 2) AS avg_daq_score
FROM rf_diagnostics_db.rf_telemetry_clean
GROUP BY 1;