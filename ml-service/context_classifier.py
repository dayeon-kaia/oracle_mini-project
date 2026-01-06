"""
Clinical Context Classifier
Rule-based 임상 상황 분류 및 Bundle/Urgency 결정
"""

def classify_clinical_context(patient_vitals: dict) -> dict:
    """
    Classify clinical context from patient vitals
    
    Args:
        patient_vitals: dict with keys like 'map', 'lactate', 'spo2', 'rr', 'urine_output'
    
    Returns:
        {
            "bundles": ["SHOCK", "SEPSIS"],
            "urgency": "STAT",
            "primary_signals": {"map": 60, "lactate": 6.4}
        }
    """
    bundles = []
    urgency = "ROUTINE"
    primary_signals = {}
    
    # Shock context
    if patient_vitals.get("map") is not None:
        map_value = patient_vitals["map"]
        if map_value < 65:
            bundles.append("SHOCK")
            primary_signals["map"] = map_value
            urgency = "STAT"
    
    # Sepsis context
    if patient_vitals.get("lactate") is not None:
        lactate = patient_vitals["lactate"]
        if lactate >= 4:
            bundles.extend(["SEPSIS", "SHOCK"])
            primary_signals["lactate"] = lactate
            urgency = "STAT"
        elif lactate >= 2:
            bundles.append("SEPSIS")
            primary_signals["lactate"] = lactate
            if urgency == "ROUTINE":
                urgency = "URGENT"
    
    # Respiratory context
    if patient_vitals.get("spo2") is not None:
        spo2 = patient_vitals["spo2"]
        if spo2 < 90:
            bundles.append("RESPIRATORY")
            primary_signals["spo2"] = spo2
            if spo2 < 85:
                urgency = "STAT"
            elif urgency == "ROUTINE":
                urgency = "URGENT"
    
    if patient_vitals.get("rr") is not None:
        rr = patient_vitals["rr"]
        if rr > 30:
            bundles.append("RESPIRATORY")
            primary_signals["rr"] = rr
            if urgency == "ROUTINE":
                urgency = "URGENT"
    
    # AKI context
    if patient_vitals.get("urine_output") is not None:
        uo = patient_vitals["urine_output"]
        if uo < 0.5:  # mL/kg/h
            bundles.append("AKI")
            primary_signals["urine_output"] = uo
            if urgency == "ROUTINE":
                urgency = "URGENT"
    
    # HTN context
    if patient_vitals.get("sbp") is not None:
        sbp = patient_vitals["sbp"]
        if sbp >= 140:
            bundles.append("HTN")
            primary_signals["sbp"] = sbp
    
    return {
        "bundles": list(set(bundles)),
        "urgency": urgency,
        "primary_signals": primary_signals
    }


# 테스트용
if __name__ == "__main__":
    # Test cases
    test_cases = [
        {"name": "STAT Shock", "vitals": {"map": 60, "lactate": 6.4}},
        {"name": "URGENT Respiratory", "vitals": {"spo2": 88, "rr": 32}},
        {"name": "URGENT AKI", "vitals": {"urine_output": 0.3}},
        {"name": "ROUTINE HTN", "vitals": {"sbp": 150}},
    ]
    
    for test in test_cases:
        result = classify_clinical_context(test["vitals"])
        print(f"\n{test['name']}:")
        print(f"  Vitals: {test['vitals']}")  
        print(f"  → Bundles: {result['bundles']}")
        print(f"  → Urgency: {result['urgency']}")
        print(f"  → Signals: {result['primary_signals']}")
