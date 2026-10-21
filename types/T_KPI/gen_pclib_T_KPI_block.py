# Paste into gen_pclib.py.
# 1) META:  "KPI": ("Control module (calculated value)", "AnaMon", [S88, S182, S101, MTP]),
# 2) after T("AI", ...):

T("KPI", "Calculated value / KPI: display range, ideal band, limit alarms, sim (EFC analog indicator templates)", HDR + [
    M("Cfg_ShortDesc", "STRING[12]", "Short description for compact HMI headers (max 11 chars)"),
    M("Cfg_EU", "STRING[12]", "Engineering units text"),
    M("Inp_Value", "REAL", "KPI value from calculation / owner logic (EU)"),
    M("Inp_Bad", "BOOL", "Source data bad (an input to the calculation is bad)"),
    M("Cfg_EUMin", "REAL", "Display range low (EU)", "0.0"),
    M("Cfg_EUMax", "REAL", "Display range high (EU)", "100.0"),
    M("Cfg_IdealLo", "REAL", "Ideal band low (EU), blue zone on HMI. Band off if Cfg_IdealLo >= Cfg_IdealHi", "0.0"),
    M("Cfg_IdealHi", "REAL", "Ideal band high (EU)", "0.0"),
    M("Cfg_FiltTC", "REAL", "1st-order filter time constant (s), 0 = off", "0.0"),
    M("Sim_En", "BOOL", "Simulation enabled"),
    M("Sim_Value", "REAL", "Simulated value (EU)", "0.0"),
    M("Val_PV", "REAL", "KPI value (EU) after filter / simulation - use this in logic and HMI"),
    M("Val_PVPct", "REAL", "KPI value (% of display range)"),
    M("Sts_Bad", "BOOL", "Value bad (Inp_Bad and not simulated)"),
    M("Sts_Sim", "BOOL", "Simulation active"),
    M("Sts_Quality", "INT", "0=Good 1=Uncertain (simulation) 2=Bad"),
    M("Sts_InIdeal", "BOOL", "Value inside the ideal band"),
    M("Sts_Zone", "INT", "-3=LL -2=L -1=Below ideal 0=Ideal or normal 1=Above ideal 2=H 3=HH"),
    AL("Alm_HH", "High-high alarm"),
    AL("Alm_H", "High alarm"),
    AL("Alm_L", "Low alarm"),
    AL("Alm_LL", "Low-low alarm"),
], "Core")
