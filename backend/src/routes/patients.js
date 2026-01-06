const express = require("express");
const router = express.Router();

// Mock patient data from mimic/demo_data with time-series vitals and risk trends
const MOCK_PATIENTS = {
  asof: "2026-01-05T10:10:00+09:00",
  patients: [
    {
      stay_id: "P9",
      bed_id: "Bed 1",
      icu_unit: "MICU",
      spo2_last: 84,
      rr_last: 32,
      hr_last: 112,
      map_last: 74,
      lactate_last: 2.6,
      o2_device: "HFNC",
      risk_mortality_24h: 0.36,
      risk_vent_12h: 0.78,
      risk_pressor_12h: 0.18,
      risk_level: "HIGH",
      delta_2h: { mortality: 0.07, vent: 0.15, pressor: 0.02 },
      trigger_event: "Vent_risk_high",
      vitals_trends: {
        spo2: [{ t: "-24h", v: 93 }, { t: "-18h", v: 92 }, { t: "-12h", v: 90 }, { t: "-6h", v: 88 }, { t: "-2h", v: 86 }, { t: "now", v: 84 }],
        rr: [{ t: "-24h", v: 20 }, { t: "-18h", v: 22 }, { t: "-12h", v: 24 }, { t: "-6h", v: 28 }, { t: "-2h", v: 30 }, { t: "now", v: 32 }],
        hr: [{ t: "-24h", v: 92 }, { t: "-18h", v: 96 }, { t: "-12h", v: 102 }, { t: "-6h", v: 108 }, { t: "-2h", v: 110 }, { t: "now", v: 112 }],
        map: [{ t: "-24h", v: 82 }, { t: "-18h", v: 80 }, { t: "-12h", v: 78 }, { t: "-6h", v: 76 }, { t: "-2h", v: 75 }, { t: "now", v: 74 }],
        lactate: [{ t: "-24h", v: 1.6 }, { t: "-18h", v: 1.8 }, { t: "-12h", v: 2.0 }, { t: "-6h", v: 2.2 }, { t: "-2h", v: 2.4 }, { t: "now", v: 2.6 }]
      },
      risk_timeline_24h: [
        { t: "-24h", mortality: 0.14, vent: 0.28, pressor: 0.08 },
        { t: "-18h", mortality: 0.18, vent: 0.36, pressor: 0.10 },
        { t: "-12h", mortality: 0.22, vent: 0.48, pressor: 0.12 },
        { t: "-6h", mortality: 0.28, vent: 0.62, pressor: 0.14 },
        { t: "-2h", mortality: 0.32, vent: 0.71, pressor: 0.16 },
        { t: "now", mortality: 0.36, vent: 0.78, pressor: 0.18 }
      ]
    },
    {
      stay_id: "P10",
      bed_id: "Bed 4",
      icu_unit: "SICU",
      spo2_last: 95,
      rr_last: 18,
      hr_last: 132,
      map_last: 70,
      lactate_last: 3.1,
      o2_device: "NC",
      risk_mortality_24h: 0.41,
      risk_vent_12h: 0.22,
      risk_pressor_12h: 0.54,
      risk_level: "HIGH",
      delta_2h: { mortality: 0.05, vent: 0.01, pressor: 0.16 },
      trigger_event: "Sepsis_suspected",
      vitals_trends: {
        spo2: [{ t: "-24h", v: 97 }, { t: "-18h", v: 97 }, { t: "-12h", v: 96 }, { t: "-6h", v: 96 }, { t: "-2h", v: 95 }, { t: "now", v: 95 }],
        rr: [{ t: "-24h", v: 16 }, { t: "-18h", v: 16 }, { t: "-12h", v: 17 }, { t: "-6h", v: 17 }, { t: "-2h", v: 18 }, { t: "now", v: 18 }],
        hr: [{ t: "-24h", v: 98 }, { t: "-18h", v: 104 }, { t: "-12h", v: 112 }, { t: "-6h", v: 120 }, { t: "-2h", v: 128 }, { t: "now", v: 132 }],
        map: [{ t: "-24h", v: 78 }, { t: "-18h", v: 76 }, { t: "-12h", v: 74 }, { t: "-6h", v: 72 }, { t: "-2h", v: 71 }, { t: "now", v: 70 }],
        lactate: [{ t: "-24h", v: 1.9 }, { t: "-18h", v: 2.1 }, { t: "-12h", v: 2.4 }, { t: "-6h", v: 2.7 }, { t: "-2h", v: 2.9 }, { t: "now", v: 3.1 }]
      },
      risk_timeline_24h: [
        { t: "-24h", mortality: 0.20, vent: 0.10, pressor: 0.18 },
        { t: "-18h", mortality: 0.24, vent: 0.11, pressor: 0.22 },
        { t: "-12h", mortality: 0.28, vent: 0.14, pressor: 0.30 },
        { t: "-6h", mortality: 0.34, vent: 0.18, pressor: 0.40 },
        { t: "-2h", mortality: 0.38, vent: 0.20, pressor: 0.48 },
        { t: "now", mortality: 0.41, vent: 0.22, pressor: 0.54 }
      ]
    },
    {
      stay_id: "P11",
      bed_id: "Bed 6",
      icu_unit: "CCU",
      spo2_last: 96,
      rr_last: 20,
      hr_last: 88,
      map_last: 54,
      lactate_last: 4.8,
      o2_device: "Room air",
      risk_mortality_24h: 0.52,
      risk_vent_12h: 0.12,
      risk_pressor_12h: 0.83,
      risk_level: "HIGH",
      delta_2h: { mortality: 0.08, vent: 0.00, pressor: 0.21 },
      trigger_event: "Pressor_risk_high",
      vitals_trends: {
        spo2: [{ t: "-24h", v: 98 }, { t: "-18h", v: 98 }, { t: "-12h", v: 97 }, { t: "-6h", v: 97 }, { t: "-2h", v: 96 }, { t: "now", v: 96 }],
        rr: [{ t: "-24h", v: 18 }, { t: "-18h", v: 18 }, { t: "-12h", v: 19 }, { t: "-6h", v: 19 }, { t: "-2h", v: 20 }, { t: "now", v: 20 }],
        hr: [{ t: "-24h", v: 78 }, { t: "-18h", v: 80 }, { t: "-12h", v: 82 }, { t: "-6h", v: 84 }, { t: "-2h", v: 86 }, { t: "now", v: 88 }],
        map: [{ t: "-24h", v: 70 }, { t: "-18h", v: 66 }, { t: "-12h", v: 62 }, { t: "-6h", v: 58 }, { t: "-2h", v: 56 }, { t: "now", v: 54 }],
        lactate: [{ t: "-24h", v: 2.2 }, { t: "-18h", v: 2.8 }, { t: "-12h", v: 3.4 }, { t: "-6h", v: 4.1 }, { t: "-2h", v: 4.5 }, { t: "now", v: 4.8 }]
      },
      risk_timeline_24h: [
        { t: "-24h", mortality: 0.24, vent: 0.06, pressor: 0.22 },
        { t: "-18h", mortality: 0.30, vent: 0.07, pressor: 0.32 },
        { t: "-12h", mortality: 0.36, vent: 0.08, pressor: 0.50 },
        { t: "-6h", mortality: 0.44, vent: 0.10, pressor: 0.68 },
        { t: "-2h", mortality: 0.48, vent: 0.11, pressor: 0.77 },
        { t: "now", mortality: 0.52, vent: 0.12, pressor: 0.83 }
      ]
    },
    {
      stay_id: "P12",
      bed_id: "Bed 10",
      icu_unit: "MICU",
      spo2_last: 98,
      rr_last: 14,
      hr_last: 76,
      map_last: 90,
      lactate_last: 1.1,
      o2_device: "Room air",
      risk_mortality_24h: 0.03,
      risk_vent_12h: 0.02,
      risk_pressor_12h: 0.02,
      risk_level: "LOW",
      delta_2h: { mortality: 0.00, vent: 0.00, pressor: 0.00 },
      trigger_event: "None",
      vitals_trends: {
        spo2: [{ t: "-24h", v: 98 }, { t: "-18h", v: 98 }, { t: "-12h", v: 98 }, { t: "-6h", v: 98 }, { t: "-2h", v: 98 }, { t: "now", v: 98 }],
        rr: [{ t: "-24h", v: 14 }, { t: "-18h", v: 14 }, { t: "-12h", v: 14 }, { t: "-6h", v: 14 }, { t: "-2h", v: 14 }, { t: "now", v: 14 }],
        hr: [{ t: "-24h", v: 78 }, { t: "-18h", v: 77 }, { t: "-12h", v: 76 }, { t: "-6h", v: 76 }, { t: "-2h", v: 76 }, { t: "now", v: 76 }],
        map: [{ t: "-24h", v: 92 }, { t: "-18h", v: 91 }, { t: "-12h", v: 90 }, { t: "-6h", v: 90 }, { t: "-2h", v: 90 }, { t: "now", v: 90 }],
        lactate: [{ t: "-24h", v: 1.2 }, { t: "-18h", v: 1.2 }, { t: "-12h", v: 1.1 }, { t: "-6h", v: 1.1 }, { t: "-2h", v: 1.1 }, { t: "now", v: 1.1 }]
      },
      risk_timeline_24h: [
        { t: "-24h", mortality: 0.04, vent: 0.03, pressor: 0.03 },
        { t: "-18h", mortality: 0.04, vent: 0.03, pressor: 0.03 },
        { t: "-12h", mortality: 0.03, vent: 0.02, pressor: 0.02 },
        { t: "-6h", mortality: 0.03, vent: 0.02, pressor: 0.02 },
        { t: "-2h", mortality: 0.03, vent: 0.02, pressor: 0.02 },
        { t: "now", mortality: 0.03, vent: 0.02, pressor: 0.02 }
      ]
    },
    {
      stay_id: "P13",
      bed_id: "Bed 15",
      icu_unit: "SICU",
      spo2_last: 90,
      rr_last: 28,
      hr_last: 108,
      map_last: 66,
      lactate_last: 2.0,
      o2_device: "NIV",
      risk_mortality_24h: 0.29,
      risk_vent_12h: 0.66,
      risk_pressor_12h: 0.24,
      risk_level: "MEDIUM",
      delta_2h: { mortality: 0.04, vent: 0.11, pressor: 0.03 },
      trigger_event: "Vent_risk_medium",
      vitals_trends: {
        spo2: [{ t: "-24h", v: 95 }, { t: "-18h", v: 94 }, { t: "-12h", v: 93 }, { t: "-6h", v: 92 }, { t: "-2h", v: 91 }, { t: "now", v: 90 }],
        rr: [{ t: "-24h", v: 20 }, { t: "-18h", v: 22 }, { t: "-12h", v: 24 }, { t: "-6h", v: 26 }, { t: "-2h", v: 27 }, { t: "now", v: 28 }],
        hr: [{ t: "-24h", v: 92 }, { t: "-18h", v: 96 }, { t: "-12h", v: 100 }, { t: "-6h", v: 104 }, { t: "-2h", v: 106 }, { t: "now", v: 108 }],
        map: [{ t: "-24h", v: 74 }, { t: "-18h", v: 72 }, { t: "-12h", v: 70 }, { t: "-6h", v: 68 }, { t: "-2h", v: 67 }, { t: "now", v: 66 }],
        lactate: [{ t: "-24h", v: 1.4 }, { t: "-18h", v: 1.6 }, { t: "-12h", v: 1.8 }, { t: "-6h", v: 1.9 }, { t: "-2h", v: 2.0 }, { t: "now", v: 2.0 }]
      },
      risk_timeline_24h: [
        { t: "-24h", mortality: 0.14, vent: 0.28, pressor: 0.12 },
        { t: "-18h", mortality: 0.18, vent: 0.36, pressor: 0.14 },
        { t: "-12h", mortality: 0.22, vent: 0.45, pressor: 0.16 },
        { t: "-6h", mortality: 0.26, vent: 0.56, pressor: 0.20 },
        { t: "-2h", mortality: 0.28, vent: 0.62, pressor: 0.22 },
        { t: "now", mortality: 0.29, vent: 0.66, pressor: 0.24 }
      ]
    },
    {
      stay_id: "P14",
      bed_id: "Bed 19",
      icu_unit: "MICU",
      spo2_last: 92,
      rr_last: 22,
      hr_last: 118,
      map_last: 63,
      lactate_last: 5.7,
      o2_device: "NC",
      risk_mortality_24h: 0.74,
      risk_vent_12h: 0.30,
      risk_pressor_12h: 0.79,
      risk_level: "CRITICAL",
      delta_2h: { mortality: 0.10, vent: 0.02, pressor: 0.14 },
      trigger_event: "Shock_high",
      vitals_trends: {
        spo2: [{ t: "-24h", v: 96 }, { t: "-18h", v: 95 }, { t: "-12h", v: 95 }, { t: "-6h", v: 94 }, { t: "-2h", v: 93 }, { t: "now", v: 92 }],
        rr: [{ t: "-24h", v: 18 }, { t: "-18h", v: 19 }, { t: "-12h", v: 20 }, { t: "-6h", v: 21 }, { t: "-2h", v: 22 }, { t: "now", v: 22 }],
        hr: [{ t: "-24h", v: 102 }, { t: "-18h", v: 106 }, { t: "-12h", v: 110 }, { t: "-6h", v: 114 }, { t: "-2h", v: 116 }, { t: "now", v: 118 }],
        map: [{ t: "-24h", v: 76 }, { t: "-18h", v: 72 }, { t: "-12h", v: 70 }, { t: "-6h", v: 66 }, { t: "-2h", v: 64 }, { t: "now", v: 63 }],
        lactate: [{ t: "-24h", v: 2.6 }, { t: "-18h", v: 3.2 }, { t: "-12h", v: 4.1 }, { t: "-6h", v: 4.9 }, { t: "-2h", v: 5.4 }, { t: "now", v: 5.7 }]
      },
      risk_timeline_24h: [
        { t: "-24h", mortality: 0.40, vent: 0.18, pressor: 0.42 },
        { t: "-18h", mortality: 0.46, vent: 0.20, pressor: 0.50 },
        { t: "-12h", mortality: 0.54, vent: 0.24, pressor: 0.60 },
        { t: "-6h", mortality: 0.64, vent: 0.27, pressor: 0.70 },
        { t: "-2h", mortality: 0.70, vent: 0.29, pressor: 0.76 },
        { t: "now", mortality: 0.74, vent: 0.30, pressor: 0.79 }
      ]
    },
    {
      stay_id: "P15",
      bed_id: "Bed 22",
      icu_unit: "CCU",
      spo2_last: 88,
      rr_last: 30,
      hr_last: 124,
      map_last: 61,
      lactate_last: 6.4,
      o2_device: "MV",
      risk_mortality_24h: 0.89,
      risk_vent_12h: 0.97,
      risk_pressor_12h: 0.86,
      risk_level: "CRITICAL",
      delta_2h: { mortality: 0.13, vent: 0.06, pressor: 0.09 },
      trigger_event: "Mortality_high",
      vitals_trends: {
        spo2: [{ t: "-24h", v: 95 }, { t: "-18h", v: 93 }, { t: "-12h", v: 92 }, { t: "-6h", v: 90 }, { t: "-2h", v: 89 }, { t: "now", v: 88 }],
        rr: [{ t: "-24h", v: 20 }, { t: "-18h", v: 22 }, { t: "-12h", v: 24 }, { t: "-6h", v: 28 }, { t: "-2h", v: 29 }, { t: "now", v: 30 }],
        hr: [{ t: "-24h", v: 96 }, { t: "-18h", v: 104 }, { t: "-12h", v: 112 }, { t: "-6h", v: 118 }, { t: "-2h", v: 122 }, { t: "now", v: 124 }],
        map: [{ t: "-24h", v: 74 }, { t: "-18h", v: 70 }, { t: "-12h", v: 68 }, { t: "-6h", v: 64 }, { t: "-2h", v: 62 }, { t: "now", v: 61 }],
        lactate: [{ t: "-24h", v: 2.8 }, { t: "-18h", v: 3.6 }, { t: "-12h", v: 4.6 }, { t: "-6h", v: 5.4 }, { t: "-2h", v: 6.0 }, { t: "now", v: 6.4 }]
      },
      risk_timeline_24h: [
        { t: "-24h", mortality: 0.42, vent: 0.50, pressor: 0.44 },
        { t: "-18h", mortality: 0.54, vent: 0.62, pressor: 0.56 },
        { t: "-12h", mortality: 0.66, vent: 0.76, pressor: 0.68 },
        { t: "-6h", mortality: 0.78, vent: 0.88, pressor: 0.78 },
        { t: "-2h", mortality: 0.84, vent: 0.94, pressor: 0.83 },
        { t: "now", mortality: 0.89, vent: 0.97, pressor: 0.86 }
      ]
    },
    {
      stay_id: "P16",
      bed_id: "Bed 27",
      icu_unit: "MICU",
      spo2_last: 94,
      rr_last: 24,
      hr_last: 96,
      map_last: 69,
      lactate_last: 2.9,
      o2_device: "NC",
      risk_mortality_24h: 0.18,
      risk_vent_12h: 0.27,
      risk_pressor_12h: 0.33,
      risk_level: "MEDIUM",
      delta_2h: { mortality: 0.03, vent: 0.04, pressor: 0.07 },
      trigger_event: "Watch",
      vitals_trends: {
        spo2: [{ t: "-24h", v: 96 }, { t: "-18h", v: 96 }, { t: "-12h", v: 95 }, { t: "-6h", v: 95 }, { t: "-2h", v: 94 }, { t: "now", v: 94 }],
        rr: [{ t: "-24h", v: 18 }, { t: "-18h", v: 19 }, { t: "-12h", v: 20 }, { t: "-6h", v: 22 }, { t: "-2h", v: 23 }, { t: "now", v: 24 }],
        hr: [{ t: "-24h", v: 86 }, { t: "-18h", v: 88 }, { t: "-12h", v: 90 }, { t: "-6h", v: 92 }, { t: "-2h", v: 94 }, { t: "now", v: 96 }],
        map: [{ t: "-24h", v: 78 }, { t: "-18h", v: 76 }, { t: "-12h", v: 74 }, { t: "-6h", v: 72 }, { t: "-2h", v: 70 }, { t: "now", v: 69 }],
        lactate: [{ t: "-24h", v: 1.8 }, { t: "-18h", v: 2.0 }, { t: "-12h", v: 2.2 }, { t: "-6h", v: 2.5 }, { t: "-2h", v: 2.7 }, { t: "now", v: 2.9 }]
      },
      risk_timeline_24h: [
        { t: "-24h", mortality: 0.10, vent: 0.12, pressor: 0.12 },
        { t: "-18h", mortality: 0.12, vent: 0.14, pressor: 0.16 },
        { t: "-12h", mortality: 0.14, vent: 0.18, pressor: 0.20 },
        { t: "-6h", mortality: 0.16, vent: 0.22, pressor: 0.26 },
        { t: "-2h", mortality: 0.17, vent: 0.25, pressor: 0.30 },
        { t: "now", mortality: 0.18, vent: 0.27, pressor: 0.33 }
      ]
    }
  ]
};

// GET /api/patients - Get all patients
router.get("/", (req, res) => {
  res.json(MOCK_PATIENTS);
});

// GET /api/patients/:stay_id - Get specific patient
router.get("/:stay_id", (req, res) => {
  const patient = MOCK_PATIENTS.patients.find(
    (p) => p.stay_id === req.params.stay_id
  );

  if (!patient) {
    return res.status(404).json({ error: "Patient not found" });
  }

  res.json(patient);
});

module.exports = router;
