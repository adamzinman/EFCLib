# T_KPI (proposed for EFCLib v1)

Calculated value / KPI type for the EFC_AnalogIndicators templates (A-D). Modelled on T_AI:
same HDR, Cfg_EU, Cfg_EUMin/Max, Sim_, Val_PV, Sts_Quality and Alm_HH/H/L/LL (T_AlmLim),
without the raw-channel members (Inp_Raw, raw scaling, NE43, NE107, ROC) and with:

- Cfg_ShortDesc  STRING[12]  compact headers (options C/D)
- Cfg_IdealLo/Hi REAL        blue ideal band; off when Lo >= Hi (default 0/0 = off)
- Inp_Value / Inp_Bad        written by the calculation logic
- Sts_InIdeal, Sts_Zone      band status for logic and reporting

Files
- gen_pclib_T_KPI_block.py   paste into gen_pclib.py, then regenerate (xdd, Ignition JSON, CSV, README)
- T_KPI_Ignition81.json      preliminary UDT, same conventions as PCLib_Ignition81.json (PCLib folder,
                             OPCServer/PathPrefix/BaseTag, nested PCLib/T_AlmLim). Needs PCLib/T_AlmLim
                             imported first. Replace with the generator output once regenerated.
- pclib-T_KPI.tex            appendix table for pclib-data-types.tex (after T_AI)

Still needed: FB_KPI (filter, sim, quality, zone, alarm conditions -> FB_AlmLim) in gen_dfb.py.
