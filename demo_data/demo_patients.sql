-- Create the table for the demo layer
CREATE TABLE icu_current_status (
    stay_id VARCHAR2(20),
    bed_id VARCHAR2(20),
    spo2_last NUMBER,
    rr_last NUMBER,
    hr_last NUMBER,
    map_last NUMBER,
    lactate_last NUMBER,
    o2_device VARCHAR2(50),
    risk_mortality_24h NUMBER,
    risk_vent_12h NUMBER,
    risk_pressor_12h NUMBER,
    trigger_event VARCHAR2(50)
);

-- Insert data using INSERT ALL for efficiency
INSERT ALL
  INTO icu_current_status (stay_id, bed_id, spo2_last, rr_last, hr_last, map_last, lactate_last, o2_device, risk_mortality_24h, risk_vent_12h, risk_pressor_12h, trigger_event)
  VALUES ('P1','Bed 3',86,26,104,72,1.9,'HFNC',0.28,0.55,0.12,'Vent_risk_medium')
  INTO icu_current_status (stay_id, bed_id, spo2_last, rr_last, hr_last, map_last, lactate_last, o2_device, risk_mortality_24h, risk_vent_12h, risk_pressor_12h, trigger_event)
  VALUES ('P2','Bed 7',91,34,118,75,2.2,'NIV',0.42,0.82,0.20,'Vent_risk_high')
  INTO icu_current_status (stay_id, bed_id, spo2_last, rr_last, hr_last, map_last, lactate_last, o2_device, risk_mortality_24h, risk_vent_12h, risk_pressor_12h, trigger_event)
  VALUES ('P3','Bed 12',94,22,122,58,4.6,'NC',0.48,0.18,0.87,'Pressor_risk_high')
  INTO icu_current_status (stay_id, bed_id, spo2_last, rr_last, hr_last, map_last, lactate_last, o2_device, risk_mortality_24h, risk_vent_12h, risk_pressor_12h, trigger_event)
  VALUES ('P4','Bed 18',97,16,82,85,1.2,'Room air',0.04,0.03,0.02,'None')
  INTO icu_current_status (stay_id, bed_id, spo2_last, rr_last, hr_last, map_last, lactate_last, o2_device, risk_mortality_24h, risk_vent_12h, risk_pressor_12h, trigger_event)
  VALUES ('P5','Bed 21',89,30,128,62,6.1,'MV',0.91,0.95,0.88,'Mortality_high')
  INTO icu_current_status (stay_id, bed_id, spo2_last, rr_last, hr_last, map_last, lactate_last, o2_device, risk_mortality_24h, risk_vent_12h, risk_pressor_12h, trigger_event)
  VALUES ('P6','Bed 25',93,24,102,68,2.8,'NC',0.22,0.35,0.31,'Watch')
SELECT 1 FROM dual;

COMMIT;
