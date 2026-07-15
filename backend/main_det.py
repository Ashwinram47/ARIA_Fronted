assets = [
    {"tag": "P-101", "asset_type": "Pump", "system": "Cooling Water", "pid": True, 
     "datasheet": False, "certificate": True, "sap": True, "punch": "Closed"},
    {"tag": "V-201", "asset_type": "Valve", "system": "Process System", "pid": True, 
     "datasheet": True, "certificate": False, "sap": True, "punch": "Closed"},
    {"tag": "T-301", "asset_type": "Tank", "system": "Storage System", "pid": True, 
     "datasheet": True, "certificate": True, "sap": False, "punch": "Closed"},
    {"tag": "C-401", "asset_type": "Compressor", "system": "Air System", "pid": True, 
     "datasheet": True, "certificate": True, "sap": True, "punch": "Open Cat A"},
    {"tag": "PL-501", "asset_type": "Pipeline", "system": "Utility System", "pid": True, 
     "datasheet": True, "certificate": True, "sap": True, "punch": "Closed"}
]

def check_asset(asset):
    gaps = []
    if not asset["pid"]: gaps.append("P&ID drawing is missing")
    if not asset["datasheet"]: gaps.append("Datasheet is missing")
    if not asset["certificate"]: gaps.append("Certificate is missing")
    if not asset["sap"]: gaps.append("SAP tag is missing")

    if asset["punch"] == "Open Cat A":
        return {"tag": asset["tag"], "asset_type": asset["asset_type"], "system": asset["system"],
            "status": "Blocked", "reason": "Category A punch item is open",
            "action": "Construction must close the Category A punch item before handover"}
    
    #category b -> verification required

    if gaps:
        return {"tag": asset["tag"], "asset_type": asset["asset_type"], "system": asset["system"],
            "status": "Not Ready", "reason": ", ".join(gaps),
            "action": "Responsible team must resolve all missing items before handover"}
    
    return {"tag": asset["tag"], "asset_type": asset["asset_type"], "system": asset["system"],
        "status": "Ready", "reason": "All required records are available and punch is closed",
        "action": "Asset can proceed to handover review"}

def print_result(result):
    print("=" * 50)
    print(f"Asset : {result['tag']} | {result['asset_type']} | {result['system']}")
    print(f"Status : {result['status'].upper()}")
    print(f"Reason : {result['reason']}")
    print(f"Action : {result['action']}")
    print("=" * 50)

    # does AI even need to be used? perhaps have 2 programs with deterministic programming vs AI

for asset in assets:
    result = check_asset(asset)
    print_result(result)