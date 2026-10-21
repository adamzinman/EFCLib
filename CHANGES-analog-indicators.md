# Drop-in: analog indicator templates + T_KPI (2026-10-20)

Unzip at the efc-ignition-library repo root. Adds:
- projects/EFC_AnalogIndicators/  Ignition 8.1 project (parent EFC_Styles): EFC/AnalogIndicator/A_RangeBar,
  B_PointerScale, C_CompactRow, D_MiniColumn, _Examples; Indicator/Analog/* style classes;
  gen_analog_indicators.py (source of truth). Views bind to PCLib T_KPI via the TagPath param.
- types/T_KPI/  proposed EFCLib v1 type (generator block, preliminary Ignition UDT, appendix table).
- mockups/analog-indicator-options.md, steward/docs/<view>.md.

Replaces the earlier draft types/T_AnalogIn (delete it if you unzipped the first drop-in).
Known gap: no dynamic window (long-press openDock) yet; needs the dock id.
