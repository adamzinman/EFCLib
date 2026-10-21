"""
P&ID symbol geometry for the EFC Perspective library (v2).
ISA-5.1 symbol shapes, ISA-101 grayscale rendering.

Each symbol: Sym(name, category, vb=(w, h), native=px_width_at_1080p, elems=[...], level=(x,y,w,h) or None)
Element roles (decide colors + bindings):
  body    fill = state color, stroke = alarm color/weight          (equipment that runs / valve body)
  head    fill = command color (actuator head), stroke = alarm
  shell   fill = vessel shell (neutral, red on fault), stroke = alarm
  face    fill = white, stroke = alarm                               (instrument bubbles, primary elements)
  outline fill none, stroke = alarm
  plain   fill = white, stroke = detail (static)
  detail  stroke only, thin, static          (add dash="4 3" for dashed)
  dark    solid dark fill, static
  pipe    process-line stub, static
  level   level fill (vessels), y/height bound to params.level
"""

# ------------------------------------------------------------------ palette (matches EFC_Styles PALETTE)
PALETTE = {
    "running": "#FFFFFF", "stopped": "#9E9E9E", "transition": "#C4C4C4", "fault": "#D50000",
    "shell": "#EBEBEB", "face": "#FFFFFF", "plain": "#FFFFFF",
    "outline": "#262626", "detail": "#262626", "dark": "#262626", "pipe": "#333333",
    "level": "#7F8FA6",
    "alarm": {1: "#00A3E0", 2: "#FFD200", 3: "#FF7A00", 4: "#D50000"},
    "utility": "#595959",
}
# stroke weights in screen px at 1080p (converted per symbol to viewBox units)
W_OUTLINE, W_ALARM, W_DETAIL, W_PIPE = 1.5, 3.0, 1.0, 2.0


class E:
    def __init__(self, role, kind, **a):
        self.role, self.kind, self.a = role, kind, a


def P(role, d, **kw): return E(role, "path", d=d, **kw)
def C(role, cx, cy, r, **kw): return E(role, "circle", cx=cx, cy=cy, r=r, **kw)
def R(role, x, y, w, h, rx=0, **kw): return E(role, "rect", x=x, y=y, w=w, h=h, rx=rx, **kw)


class Sym:
    def __init__(self, name, cat, vb, native, elems, level=None, desc="", command=False):
        self.name, self.cat, self.vb, self.native, self.elems = name, cat, vb, native, elems
        self.level, self.desc = level, desc
        self.command = command or any(e.role == "head" for e in elems)

    @property
    def k(self):  # viewBox units per screen px
        return self.vb[0] / self.native

    @property
    def size(self):
        return self.native, round(self.native * self.vb[1] / self.vb[0])

    @property
    def roles(self):
        return {e.role for e in self.elems}

    @property
    def bindable(self):
        return bool(self.roles & {"body", "head", "shell", "face", "outline", "level"})


SYMS = []
def add(*a, **kw):
    s = Sym(*a, **kw); SYMS.append(s); return s

def circ(cx, cy, r):  # circle as path (lets several circles share one element)
    return f"M{cx-r} {cy} A{r} {r} 0 1 0 {cx+r} {cy} A{r} {r} 0 1 0 {cx-r} {cy} Z"

# =================================================================== ROTATING  (vb 100x100)
BASE = P("detail", "M32 74 L24 92 H76 L68 74")
CENT_BODY = "M50 20 H90 V33 H74.72 A30 30 0 1 1 50 20 Z"     # circle + tangential discharge
SUCT = P("pipe", "M2 50 H20"); DISCH = P("pipe", "M90 26.5 H98")
SIDE = [P("pipe", "M2 50 H20"), P("pipe", "M80 50 H98")]
RC = "Rotating"

add("Pump_Centrifugal", RC, (100, 100), 56, [SUCT, DISCH, P("body", CENT_BODY), BASE], desc="Centrifugal pump, suction left, tangential discharge top-right")
add("Pump_Inline", RC, (100, 100), 56, [P("pipe", "M2 56 H24"), P("pipe", "M76 56 H98"), C("body", 50, 56, 26),
    R("plain", 38, 8, 24, 16, 2), P("detail", "M50 24 V30")], desc="Vertical in-line pump with motor")
add("Pump_Gear", RC, (100, 100), 56, SIDE + [C("body", 50, 50, 30), C("detail", 40, 50, 9), C("detail", 60, 50, 9), BASE], desc="Gear (rotary PD) pump")
add("Pump_Screw", RC, (100, 100), 56, SIDE + [C("body", 50, 50, 30),
    P("detail", "M26 50 L31 42 L37 58 L43 42 L49 58 L55 42 L61 58 L67 42 L73 50"), BASE], desc="Screw pump")
add("Pump_Progressive_Cavity", RC, (100, 100), 56, [P("pipe", "M2 50 H14"), P("pipe", "M86 50 H98"),
    R("body", 14, 36, 72, 28, 14), P("detail", "M22 50 Q29 38 36 50 T50 50 T64 50 T78 50")], desc="Progressive cavity pump")
add("Pump_Diaphragm", RC, (100, 100), 56, SIDE + [C("body", 50, 50, 30), P("detail", "M28 60 Q50 28 72 60"), BASE], desc="Diaphragm (AODD) pump")
add("Pump_Reciprocating", RC, (100, 100), 56, [P("pipe", "M36 70 V96"), P("pipe", "M36 30 V4"),
    R("body", 18, 30, 56, 40), P("detail", "M48 34 V66 M48 50 H96")], desc="Reciprocating / piston pump")
add("Pump_Metering", RC, (100, 100), 56, SIDE + [C("body", 50, 50, 30), P("detail", "M30 70 L68 32 M58 32 H68 V42"), BASE], desc="Metering pump (adjustable)")
add("Pump_Submersible", RC, (100, 100), 56, [P("pipe", "M50 30 V4"), R("body", 36, 30, 28, 60, 6), P("detail", "M36 60 H64")], desc="Submersible pump")
add("Pump_Vacuum", RC, (100, 100), 56, SIDE + [C("body", 50, 50, 30), C("detail", 56, 50, 17), BASE], desc="Liquid-ring vacuum pump")
add("Pump_Peristaltic", RC, (100, 100), 56, SIDE + [C("body", 50, 50, 30), C("detail", 50, 50, 16),
    C("dark", 50, 34, 4), C("dark", 64, 58, 4), C("dark", 36, 58, 4), BASE], desc="Peristaltic / hose pump")

CSIDE = [P("pipe", "M2 50 H16"), P("pipe", "M84 50 H98")]
CONV = P("detail", "M24 30 L76 41 M24 70 L76 59")
add("Compressor_Centrifugal", RC, (100, 100), 64, CSIDE + [C("body", 50, 50, 34), CONV], desc="Centrifugal / dynamic compressor")
add("Compressor_Reciprocating", RC, (100, 100), 64, [P("pipe", "M2 50 H14"), P("pipe", "M86 50 H98"), R("body", 14, 28, 72, 44),
    P("detail", "M18 32 L82 42 M18 68 L82 58")], desc="Reciprocating compressor")
add("Compressor_Screw", RC, (100, 100), 64, CSIDE + [C("body", 50, 50, 34), CONV,
    P("detail", "M34 50 L39 45 L44 55 L49 45 L54 55 L59 45 L64 50")], desc="Rotary screw compressor")
add("Compressor_Diaphragm", RC, (100, 100), 64, CSIDE + [C("body", 50, 50, 34), CONV,
    P("detail", "M32 58 Q50 36 68 58", width=2.0)], desc="Diaphragm compressor")
add("Blower_Rotary_Lobe", RC, (100, 100), 56, SIDE + [C("body", 50, 50, 30),
    P("detail", f"{circ(41, 50, 9)} {circ(59, 50, 9)}"), BASE], desc="Rotary lobe (Roots) blower")
add("Fan_Centrifugal", RC, (100, 100), 56, [SUCT, DISCH, P("body", CENT_BODY),
    P("detail", "M50 38 Q60 42 60 52 M38 50 Q42 40 52 40 M50 62 Q40 58 40 48"), BASE], desc="Centrifugal fan / blower")
add("Fan_Axial", RC, (100, 100), 56, [R("outline", 8, 24, 84, 52),
    P("body", "M50 50 C44 40 42 30 50 27 C57 30 56 40 50 50 C56 60 58 70 50 73 C43 70 44 60 50 50 Z"),
    C("dark", 50, 50, 3)], desc="Axial fan in duct")
add("Motor", RC, (100, 100), 48, [P("pipe", "M80 50 H98"), C("body", 50, 50, 30),
    P("detail", "M37 63 V37 L50 55 L63 37 V63", width=1.5)], desc="Electric motor")
add("Drive_VFD", RC, (100, 100), 48, [R("body", 18, 24, 64, 52, 3),
    P("detail", "M28 50 Q36 34 44 50 T60 50 T76 50"), P("detail", "M26 66 H74")], desc="Variable frequency drive")
add("Agitator", RC, (100, 100), 56, [C("body", 50, 18, 13), P("detail", "M43 23 V13 L50 20 L57 13 V23"),
    P("detail", "M50 31 V86", width=1.5), P("detail", "M30 86 H70 M30 80 V92 M70 80 V92", width=1.5)], desc="Top-entry agitator / mixer")
add("Mixer_Static", RC, (100, 100), 56, [P("pipe", "M0 50 H8"), P("pipe", "M92 50 H100"), R("body", 8, 38, 84, 24),
    P("detail", "M14 62 L22 38 L30 62 L38 38 L46 62 L54 38 L62 62 L70 38 L78 62 L86 38")], desc="In-line static mixer")
add("Turbine", RC, (100, 100), 56, [P("pipe", "M2 50 H28"), P("pipe", "M72 50 H98"), P("body", "M28 34 L72 18 V82 L28 66 Z")], desc="Turbine / expander")
add("Conveyor_Belt", RC, (200, 60), 112, [P("body", "M24 18 H176 A12 12 0 0 1 176 42 H24 A12 12 0 0 1 24 18 Z"),
    C("detail", 24, 30, 8), C("detail", 176, 30, 8), C("dark", 70, 30, 3), C("dark", 100, 30, 3), C("dark", 130, 30, 3)], desc="Belt conveyor")
add("Conveyor_Screw", RC, (200, 60), 112, [P("pipe", "M24 18 V2"), P("pipe", "M176 42 V58"), R("body", 10, 18, 180, 24),
    P("detail", " ".join(f"M{x} 42 L{x+10} 18" for x in range(20, 180, 14)))], desc="Screw conveyor / auger")
add("RotaryValve_Airlock", RC, (100, 100), 48, [P("pipe", "M50 2 V28"), P("pipe", "M50 72 V98"), R("body", 28, 28, 44, 44),
    C("detail", 50, 50, 16), P("detail", "M50 34 V66 M34 50 H66 M39 39 L61 61 M61 39 L39 61")], desc="Rotary airlock valve / feeder")

# =================================================================== VALVES  (vb 100x100, centerline y=70, ends x=10/90)
VC = "Valves"
BOW = "M10 56 L90 84 L90 56 L10 84 Z"
DOWN = "M50 70 L36 98 H64 Z"
BODIES = {
    "Gate":      lambda: [P("body", BOW)],
    "Globe":     lambda: [P("body", BOW), C("dark", 50, 70, 6)],
    "Ball":      lambda: [P("body", BOW), C("body", 50, 70, 9)],
    "Butterfly": lambda: [P("pipe", "M12 70 H88"), P("outline", "M12 56 V84 M88 56 V84"), C("body", 50, 70, 10), P("detail", "M41 81 L59 59")],
    "Plug":      lambda: [P("body", BOW), R("plain", 44, 64, 12, 12)],
    "Needle":    lambda: [P("body", BOW), P("dark", "M45 48 H55 L50 66 Z")],
    "Diaphragm": lambda: [P("body", BOW), P("detail", "M28 52 Q50 36 72 52", width=1.5)],
    "Pinch":     lambda: [P("body", "M10 56 Q50 76 90 56 V84 Q50 64 10 84 Z")],
    "Knife":     lambda: [P("body", BOW), P("detail", "M50 70 V46 M43 46 H57")],
    "Check":     lambda: [P("body", BOW), P("dark", "M90 56 L50 70 L90 84 Z")],
    "ThreeWay":  lambda: [P("pipe", "M50 98 V100"), P("body", f"{BOW} {DOWN}")],
    "FourWay":   lambda: [P("body", f"{BOW} {DOWN} M50 70 L36 42 H64 Z")],
    "Angle":     lambda: [P("body", f"M10 56 L50 70 L10 84 Z {DOWN}")],
    "Damper":    lambda: [R("body", 12, 56, 76, 28), P("detail", "M24 81 L40 59 M42 81 L58 59 M60 81 L76 59")],
}
ACTUATORS = {
    "Diaphragm":  lambda top=56: [P("detail", f"M50 {top} V36", width=1.5), P("head", "M28 36 Q50 6 72 36 Z")],
    "Piston":     lambda top=56: [P("detail", f"M50 {top} V38", width=1.5), R("head", 32, 16, 36, 22), P("detail", "M32 27 H68")],
    "Solenoid":   lambda top=56: [P("detail", f"M50 {top} V42", width=1.5), R("head", 34, 14, 32, 28),
                                  P("detail", "M57 21 H45 Q42 21 42 24.5 Q42 28 45 28 H55 Q58 28 58 31.5 Q58 35 55 35 H43", width=1.5)],
    "Motor":      lambda top=56: [P("detail", f"M50 {top} V39", width=1.5), C("head", 50, 24, 15), P("detail", "M42 31 V17 L50 26 L58 17 V31", width=1.5)],
    "Hydraulic":  lambda top=56: [P("detail", f"M50 {top} V38", width=1.5), R("head", 32, 16, 36, 22), P("detail", "M43 20 V34 M57 20 V34 M43 27 H57", width=1.5)],
    "Handwheel":  lambda top=56: [P("detail", f"M50 {top} V36 M34 36 H66", width=1.5)],
}

MANUAL = [("Valve_Gate", "Gate", "Gate valve (generic manual 2-way)"), ("Valve_Globe", "Globe", "Globe valve"),
          ("Valve_Ball", "Ball", "Ball valve"), ("Valve_Butterfly", "Butterfly", "Butterfly valve"),
          ("Valve_Plug", "Plug", "Plug valve"), ("Valve_Needle", "Needle", "Needle valve"),
          ("Valve_Diaphragm", "Diaphragm", "Diaphragm valve"), ("Valve_Pinch", "Pinch", "Pinch valve"),
          ("Valve_Knife_Gate", "Knife", "Knife gate valve"), ("Valve_Check", "Check", "Check valve (flow left to right)"),
          ("Valve_ThreeWay", "ThreeWay", "3-way valve"), ("Valve_FourWay", "FourWay", "4-way valve"),
          ("Valve_Angle", "Angle", "Angle valve"), ("Damper", "Damper", "Damper / louver")]
for n, b, d in MANUAL:
    add(n, VC, (100, 100), 36, BODIES[b](), desc=d)
add("Valve_Gate_Handwheel", VC, (100, 100), 36, BODIES["Gate"]() + ACTUATORS["Handwheel"](), desc="Gate valve with handwheel")

ACTUATED = [("Valve_Control", "Globe", "Diaphragm", "Control valve, pneumatic diaphragm"),
            ("Valve_Control_Ball", "Ball", "Diaphragm", "Control ball (V-ball) valve"),
            ("Valve_Control_Butterfly", "Butterfly", "Diaphragm", "Control butterfly valve"),
            ("Valve_Control_ThreeWay", "ThreeWay", "Diaphragm", "3-way control valve"),
            ("Valve_Control_Angle", "Angle", "Diaphragm", "Angle control valve"),
            ("Valve_Control_Piston", "Globe", "Piston", "Control valve, piston actuator"),
            ("Valve_Control_Electric", "Globe", "Motor", "Control valve, electric actuator"),
            ("Valve_OnOff_Pneumatic", "Gate", "Diaphragm", "On/off valve, pneumatic (spring return)"),
            ("Valve_Ball_Piston", "Ball", "Piston", "On/off ball valve, piston actuator"),
            ("Valve_Butterfly_Piston", "Butterfly", "Piston", "On/off butterfly, piston actuator"),
            ("Valve_ThreeWay_Piston", "ThreeWay", "Piston", "3-way on/off, piston actuator"),
            ("Valve_Knife_Piston", "Knife", "Piston", "Knife gate, piston actuator"),
            ("Valve_Pinch_Pneumatic", "Pinch", "Diaphragm", "Pinch valve, pneumatic"),
            ("Valve_Diaphragm_Pneumatic", "Diaphragm", "Diaphragm", "Diaphragm valve, pneumatic"),
            ("Valve_Solenoid", "Gate", "Solenoid", "Solenoid valve"),
            ("Valve_Solenoid_ThreeWay", "ThreeWay", "Solenoid", "3-way solenoid valve"),
            ("Valve_MOV", "Gate", "Motor", "Motor-operated valve"),
            ("Valve_Ball_MOV", "Ball", "Motor", "Motor-operated ball valve"),
            ("Valve_Butterfly_MOV", "Butterfly", "Motor", "Motor-operated butterfly"),
            ("Valve_Hydraulic", "Gate", "Hydraulic", "Hydraulic-operated valve"),
            ("Damper_Actuated", "Damper", "Diaphragm", "Damper with pneumatic actuator")]
for n, b, a, d in ACTUATED:
    add(n, VC, (100, 100), 36, BODIES[b]() + ACTUATORS[a](), desc=d)

ANGLE = f"M10 56 L50 70 L10 84 Z {DOWN}"
SPRING = "M50 70 V62 L42 59 L58 53 L42 47 L58 41 L42 35 L50 32 V24"
add("Valve_Relief", VC, (100, 100), 36, [P("body", ANGLE), P("detail", SPRING, width=1.5), P("detail", "M42 24 H58", width=1.5)], desc="Pressure relief / safety valve (inlet bottom, outlet left)")
add("Valve_Relief_Vacuum", VC, (100, 100), 36, [P("body", ANGLE), P("detail", SPRING, width=1.5), P("detail", "M42 24 H58 M50 24 V14 M44 18 L50 12 L56 18", width=1.5)], desc="Pressure/vacuum relief (breather) valve")
REG_HEAD = [P("detail", "M50 56 V44", width=1.5), P("plain", "M30 44 Q50 22 70 44 Z")]
add("Regulator_Pressure", VC, (100, 100), 36, [P("body", BOW), C("dark", 50, 70, 6)] + REG_HEAD +
    [P("detail", "M70 40 H84 V62", dash="5 4", width=1.5)], desc="Self-contained pressure regulator (downstream sensing)")
add("Regulator_BackPressure", VC, (100, 100), 36, [P("body", BOW), C("dark", 50, 70, 6)] + REG_HEAD +
    [P("detail", "M30 40 H16 V62", dash="5 4", width=1.5)], desc="Back-pressure regulator (upstream sensing)")

# =================================================================== VESSELS
VS = "Vessels"
def vtank(name, shell, lvl, extra=(), desc="", vb=(100, 140), native=64, pipes=("M50 128 V138",)):
    add(name, VS, vb, native, [P("pipe", p) for p in pipes] + [P("shell", shell), R("level", *lvl)] + list(extra), level=lvl, desc=desc)

vtank("Tank_Vertical", "M20 12 H80 V128 H20 Z", (22, 14, 56, 112), desc="Vertical flat-top tank")
vtank("Tank_ConeRoof", "M20 30 L50 12 L80 30 V128 H20 Z", (22, 31, 56, 95), desc="Cone-roof atmospheric tank")
vtank("Tank_DomeRoof", "M20 30 Q50 4 80 30 V128 H20 Z", (22, 31, 56, 95), desc="Dome-roof tank")
vtank("Tank_OpenTop", "M20 14 V128 H80 V14", (22, 16, 56, 110), desc="Open-top tank")
vtank("Tank_FloatingRoof", "M20 14 V128 H80 V14", (22, 42, 56, 84), [P("detail", "M22 40 H78 M30 40 V30 M70 40 V30", width=1.5)], desc="Floating-roof tank")
vtank("Tank_ConeBottom", "M20 12 H80 V90 L56 124 H44 L20 90 Z", (22, 14, 56, 74), desc="Cone-bottom tank / silo (level over straight side)", pipes=("M50 124 V138",))
DISH = "M20 30 Q20 12 50 12 Q80 12 80 30 V110 Q80 128 50 128 Q20 128 20 110 Z"
vtank("Vessel_Vertical", DISH, (22, 30, 56, 80), desc="Vertical pressure vessel, dished heads (level over straight side)", pipes=("M50 128 V138", "M50 12 V2"))
vtank("Vessel_Jacketed", DISH, (22, 30, 56, 80), [P("detail", "M14 60 V112 Q14 134 50 134 Q86 134 86 112 V60", width=1.5)],
      desc="Jacketed vertical vessel", pipes=("M50 128 V140", "M50 12 V2"))
add("Reactor", VS, (100, 160), 72, [P("pipe", "M50 148 V160"), P("shell", "M20 50 Q20 32 50 32 Q80 32 80 50 V130 Q80 148 50 148 Q20 148 20 130 Z"),
    R("level", 22, 50, 56, 80), P("detail", "M14 80 V132 Q14 154 50 154 Q86 154 86 132 V80", width=1.5),
    C("body", 50, 14, 11), P("detail", "M44 18 V10 L50 16 L56 10 V18"), P("detail", "M50 25 V128", width=1.5),
    P("detail", "M34 126 H66 M34 120 V132 M66 120 V132", width=1.5)], level=(22, 50, 56, 80), desc="Jacketed reactor with agitator (body = agitator state)")
HORIZ = "M34 24 H126 Q150 24 150 50 Q150 76 126 76 H34 Q10 76 10 50 Q10 24 34 24 Z"
def htank(name, extra=(), desc="", lvl=(34, 26, 92, 48)):
    add(name, VS, (160, 100), 96, [P("pipe", "M50 24 V6"), P("pipe", "M110 76 V94"), P("shell", HORIZ), R("level", *lvl)] + list(extra), level=lvl, desc=desc)
htank("Vessel_Horizontal", desc="Horizontal vessel / drum (level over straight side)")
add("Drum_KO_Boot", VS, (160, 100), 96, [P("pipe", "M50 24 V6"), P("pipe", "M110 96 V100"), P("shell", HORIZ + " M100 74 V96 H120 V74"), R("level", 34, 26, 92, 48)],
    level=(34, 26, 92, 48), desc="Knock-out drum with boot")
htank("Separator_ThreePhase", [P("detail", "M112 74 V44", width=1.5)], desc="3-phase separator with weir")
add("Vessel_Spherical", VS, (100, 100), 64, [P("detail", "M26 66 L20 96 M74 66 L80 96 M40 78 L38 96 M60 78 L62 96", width=1.5),
    C("shell", 50, 44, 36)], desc="Spherical pressure vessel")
COL = "M10 22 Q10 6 30 6 Q50 6 50 22 V178 Q50 194 30 194 Q10 194 10 178 Z"
trays = " ".join(f"M{10 if i % 2 else 20} {y} H{40 if i % 2 else 50}" for i, y in enumerate(range(30, 142, 14)))
add("Column_Tray", VS, (60, 200), 40, [P("pipe", "M30 194 V200"), P("pipe", "M30 6 V0"), P("shell", COL), R("level", 12, 146, 36, 32), P("detail", trays)],
    level=(12, 146, 36, 32), desc="Trayed distillation column (level = sump)")
add("Column_Packed", VS, (60, 200), 40, [P("pipe", "M30 194 V200"), P("pipe", "M30 6 V0"), P("shell", COL), R("level", 12, 146, 36, 32),
    P("detail", "M10 34 H50 M10 74 H50 M10 34 L50 74 M50 34 L10 74 M10 90 H50 M10 130 H50 M10 90 L50 130 M50 90 L10 130")],
    level=(12, 146, 36, 32), desc="Packed column (level = sump)")
CYL = "M10 44 Q10 28 25 28 Q40 28 40 44 V128 Q40 134 34 134 H16 Q10 134 10 128 Z"
add("Gas_Cylinder", VS, (50, 140), 24, [P("shell", CYL), R("level", 12, 44, 26, 86), P("plain", "M20 28 V18 H30 V28"),
    P("detail", "M15 13 H35 M25 13 V18", width=1.5)], level=(12, 44, 26, 86), desc="Compressed gas cylinder (level = contents %)")
def cyl_at(dx):
    return f"M{10+dx} 44 Q{10+dx} 30 {25+dx} 30 Q{40+dx} 30 {40+dx} 44 V128 Q{40+dx} 134 {34+dx} 134 H{16+dx} Q{10+dx} 134 {10+dx} 128 Z"
add("Cylinder_Bank", VS, (140, 140), 64, [P("pipe", "M25 30 V14 M70 30 V14 M115 30 V14 M25 14 H136"),
    P("shell", " ".join(cyl_at(dx) for dx in (0, 45, 90)))], desc="Manifolded cylinder bank / pack")
add("Tank_Cryogenic", VS, (100, 160), 64, [P("pipe", "M50 152 V160"), P("detail", "M26 148 L22 158 M74 148 L78 158", width=1.5),
    P("shell", "M18 34 Q18 10 50 10 Q82 10 82 34 V136 Q82 152 50 152 Q18 152 18 136 Z"), R("level", 28, 38, 44, 96),
    P("detail", "M26 38 Q26 18 50 18 Q74 18 74 38 V134 Q74 144 50 144 Q26 144 26 134 Z", dash="5 4")],
    level=(28, 38, 44, 96), desc="Vacuum-insulated cryogenic storage tank")
add("Dewar", VS, (80, 100), 40, [P("shell", "M14 30 Q14 22 24 22 H32 V10 H48 V22 H56 Q66 22 66 30 V86 Q66 94 56 94 H24 Q14 94 14 86 Z"),
    R("level", 22, 34, 36, 52), P("detail", "M20 30 V84 Q20 88 24 88 H56 Q60 88 60 84 V30", dash="4 3")], level=(22, 34, 36, 52), desc="Liquid cryogen dewar")
add("Tube_Trailer", VS, (200, 80), 112, [P("detail", "M4 54 H186", width=1.5), R("shell", 20, 10, 160, 38, 8),
    P("detail", "M20 23 H180 M20 35 H180"), P("detail", f"{circ(40, 63, 7)} {circ(58, 63, 7)} {circ(150, 63, 7)} {circ(168, 63, 7)}", width=1.5)],
    desc="High-pressure tube trailer")
add("Tank_Truck", VS, (200, 80), 112, [P("detail", "M4 54 H186", width=1.5), P("plain", "M4 52 V28 H20 L26 38 V52 Z"),
    P("shell", "M44 12 H170 Q186 12 186 30 Q186 48 170 48 H44 Q30 48 30 30 Q30 12 44 12 Z"), R("level", 44, 14, 126, 32),
    P("detail", f"{circ(16, 63, 7)} {circ(140, 63, 7)} {circ(158, 63, 7)}", width=1.5)], level=(44, 14, 126, 32), desc="Tank truck / trailer")
add("Accumulator", VS, (60, 120), 32, [P("pipe", "M30 112 V120"), P("shell", "M10 28 Q10 8 30 8 Q50 8 50 28 V92 Q50 112 30 112 Q10 112 10 92 Z"),
    P("detail", "M12 60 Q30 40 48 60", width=1.5)], desc="Bladder / piston accumulator")
add("Sump_Pit", VS, (100, 100), 56, [P("shell", "M20 30 V88 H80 V30"), R("level", 22, 32, 56, 54),
    P("detail", "M4 30 H20 M80 30 H96 M8 30 L4 36 M14 30 L10 36 M88 30 L84 36 M94 30 L90 36")], level=(22, 32, 56, 54), desc="Below-grade sump / pit")
add("Tote_IBC", VS, (100, 100), 48, [P("shell", "M16 16 H84 V84 H16 Z"), R("level", 18, 18, 64, 64),
    P("detail", "M16 39 H84 M16 61 H84 M39 16 V84 M61 16 V84"), P("detail", "M10 90 H90", width=2)], level=(18, 18, 64, 64), desc="IBC tote")
add("Drum", VS, (60, 80), 28, [R("shell", 8, 8, 44, 64, 3), R("level", 10, 10, 40, 60), P("detail", "M8 30 H52 M8 50 H52")], level=(10, 10, 40, 60), desc="55-gal drum")
add("Hopper", VS, (100, 100), 56, [P("pipe", "M50 80 V98"), P("shell", "M12 14 H88 V40 L60 80 H40 L12 40 Z"), R("level", 14, 16, 72, 24)],
    level=(14, 16, 72, 24), desc="Hopper / bin (level over straight side)")

# =================================================================== HEAT TRANSFER
HT = "HeatTransfer"
add("HX_Generic", HT, (100, 100), 48, [P("pipe", "M50 16 V2"), P("pipe", "M50 84 V98"), C("shell", 50, 50, 34),
    P("pipe", "M2 50 H22 L32 30 L44 70 L56 30 L68 70 L78 50 H98")], desc="Heat exchanger, general (tube side through)")
add("HX_ShellTube", HT, (160, 80), 96, [P("pipe", "M40 16 V2"), P("pipe", "M120 64 V78"), P("pipe", "M8 28 H0 M8 52 H0"),
    P("shell", "M20 16 H138 Q154 16 154 40 Q154 64 138 64 H20 Z"), R("plain", 8, 16, 12, 48), P("detail", "M20 28 H140 M20 40 H140 M20 52 H140"),
    P("detail", "M8 40 H20")], desc="Shell & tube exchanger (2-pass)")
add("HX_UTube", HT, (160, 80), 96, [P("pipe", "M40 16 V2"), P("pipe", "M120 64 V78"), P("pipe", "M8 28 H0 M8 52 H0"),
    P("shell", "M20 16 H138 Q154 16 154 40 Q154 64 138 64 H20 Z"), R("plain", 8, 16, 12, 48),
    P("detail", "M20 28 H132 Q144 40 132 52 H20 M20 34 H128 Q136 40 128 46 H20"), P("detail", "M8 40 H20")], desc="U-tube exchanger")
add("HX_Plate", HT, (80, 100), 40, [P("pipe", "M20 24 H4 M20 76 H4 M60 24 H76 M60 76 H76"), R("shell", 20, 10, 40, 80),
    P("detail", " ".join(f"M{x} 16 V84" for x in (28, 34, 40, 46, 52))), R("dark", 18, 6, 44, 5), R("dark", 18, 89, 44, 5)], desc="Plate & frame exchanger")
add("HX_DoublePipe", HT, (160, 60), 96, [P("shell", "M10 8 H130 A22 22 0 0 1 130 52 H10"), P("detail", "M10 22 H130 A8 8 0 0 1 130 38 H10"),
    P("pipe", "M10 22 H0 M10 38 H0")], desc="Double-pipe (hairpin) exchanger")
add("HX_Kettle", HT, (160, 90), 96, [P("pipe", "M110 12 V0"), P("pipe", "M8 38 H0 M8 52 H0"),
    P("shell", "M20 30 H50 L66 12 H134 Q154 12 154 45 Q154 78 134 78 H66 L50 60 H20 Z"), R("level", 66, 42, 70, 34), R("plain", 8, 30, 12, 30),
    P("detail", "M20 40 H120 Q128 45 120 50 H20")], level=(66, 42, 70, 34), desc="Kettle reboiler")
add("AirCooler_FinFan", HT, (120, 100), 64, [P("pipe", "M10 20 H0 M110 34 H120"), R("shell", 10, 14, 100, 26),
    P("detail", "M14 27 L22 18 L30 36 L38 18 L46 36 L54 18 L62 36 L70 18 L78 36 L86 18 L94 36 L102 18 L106 27"),
    P("detail", "M14 40 V94 M106 40 V94", width=1.5), P("body", f"{circ(35, 70, 15)} {circ(85, 70, 15)}"),
    P("detail", "M35 57 V83 M22 70 H48 M85 57 V83 M72 70 H98")], desc="Air-cooled exchanger (body = fans)")
add("Heater_Electric", HT, (100, 100), 48, [P("pipe", "M2 50 H16"), P("pipe", "M84 50 H98"), P("detail", "M50 24 V8 M42 8 H58", width=1.5),
    R("body", 16, 24, 68, 52), P("detail", "M26 50 L32 38 L40 62 L48 38 L56 62 L64 38 L70 50", width=1.5)], desc="Electric heater (body = energized)")
add("Coil", HT, (100, 60), 48, [P("pipe", "M2 30 H14 C14 6 30 6 30 30 C30 54 46 54 46 30 C46 6 62 6 62 30 C62 54 78 54 78 30 C78 6 94 6 94 30 H98")],
    desc="Heating / cooling coil")
add("Fired_Heater", HT, (100, 120), 56, [P("plain", "M42 30 V6 H58 V30"), P("body", "M18 112 V52 L34 30 H66 L82 52 V112 Z"),
    P("detail", "M30 100 V60 H40 V100 H50 V60 H60 V100 H70 V60", width=1.5), P("dark", "M50 112 Q40 102 50 90 Q60 102 50 112 Z")],
    desc="Fired heater / furnace (body = firing)")
add("Boiler", HT, (100, 120), 56, [P("plain", "M62 20 V4 H74 V20"), R("body", 14, 20, 72, 92, 3), C("plain", 50, 42, 14),
    P("detail", "M30 60 H70 M30 60 V96 M70 60 V96"), P("dark", "M50 108 Q42 98 50 86 Q58 98 50 108 Z")], desc="Boiler (body = firing)")
add("Cooling_Tower", HT, (100, 110), 56, [P("detail", "M6 100 H94", width=1.5), P("shell", "M18 100 L28 30 H72 L82 100 Z"),
    R("body", 36, 14, 28, 16), P("detail", "M30 22 H70"), P("detail", "M26 62 H74 M24 74 H76", dash="4 3")], desc="Mechanical-draft cooling tower (body = fan)")
add("Chiller", HT, (100, 100), 48, [P("pipe", "M2 40 H14 M2 60 H14 M86 40 H98 M86 60 H98"), R("body", 14, 20, 72, 60, 3),
    P("detail", "M50 32 V68 M34 41 L66 59 M34 59 L66 41 M46 32 L50 36 L54 32 M46 68 L50 64 L54 68", width=1.5)], desc="Chiller / refrigeration unit")
add("Vaporizer_Ambient", HT, (100, 120), 48, [P("pipe", "M30 110 V120"), P("pipe", "M70 10 V0"), R("shell", 16, 10, 68, 100, 2),
    P("detail", " ".join(f"M{x} 14 V106" for x in (26, 36, 46, 56, 66, 76))), P("detail", "M16 18 H84 M16 102 H84", width=1.5)],
    desc="Ambient-air vaporizer (finned)")
add("Vaporizer_WaterBath", HT, (100, 100), 56, [P("pipe", "M2 70 H22 M78 30 H98"), P("shell", "M14 20 V90 H86 V20"),
    R("level", 16, 30, 68, 58), P("pipe", "M22 70 C22 50 36 50 36 70 C36 90 50 90 50 70 C50 50 64 50 64 70 C64 84 78 84 78 30")],
    level=(16, 30, 68, 58), desc="Water-bath / steam vaporizer")

# =================================================================== PROCESS (separation & misc)
PR = "Process"
VDISH = "M14 32 Q14 14 40 14 Q66 14 66 32 V96 Q66 114 40 114 Q14 114 14 96 Z"
add("Filter", PR, (100, 100), 40, [P("pipe", "M50 16 V2"), P("pipe", "M50 84 V98"), R("shell", 24, 16, 52, 68), P("detail", "M24 50 H76", dash="5 4", width=1.5)], desc="Filter, general")
add("Filter_Cartridge", PR, (80, 120), 36, [P("pipe", "M2 30 H14"), P("pipe", "M66 96 H78"), P("shell", VDISH),
    P("detail", "M24 40 H34 V100 H24 Z M46 40 H56 V100 H46 Z", dash="4 3")], desc="Cartridge filter housing")
add("Filter_Bag", PR, (80, 120), 36, [P("pipe", "M2 30 H14"), P("pipe", "M40 114 V120"), P("shell", VDISH),
    P("detail", "M22 30 V90 Q40 104 58 90 V30", dash="4 3")], desc="Bag filter housing")
add("Cyclone", PR, (100, 120), 48, [P("pipe", "M2 30 H24"), P("pipe", "M50 104 V118"), P("shell", "M24 20 H76 V54 L56 104 H44 L24 54 Z"),
    P("pipe", "M44 4 V44 H56 V4")], desc="Cyclone separator")
add("Scrubber", PR, (80, 140), 40, [P("pipe", "M40 14 V0"), P("pipe", "M40 126 V140"), P("pipe", "M2 110 H14"),
    P("shell", "M14 32 Q14 14 40 14 Q66 14 66 32 V108 Q66 126 40 126 Q14 126 14 108 Z"), R("level", 16, 104, 48, 18),
    P("detail", "M14 36 H66 M22 36 L18 46 M22 36 L26 46 M40 36 L36 46 M40 36 L44 46 M58 36 L54 46 M58 36 L62 46"),
    P("detail", "M14 56 H66 M14 88 H66 M14 56 L66 88 M66 56 L14 88")], level=(16, 104, 48, 18), desc="Packed scrubber with spray header")
TWIN = "M10 30 Q10 14 30 14 Q50 14 50 30 V112 Q50 128 30 128 Q10 128 10 112 Z M70 30 Q70 14 90 14 Q110 14 110 30 V112 Q110 128 90 128 Q70 128 70 112 Z"
add("Dryer_Desiccant", PR, (120, 140), 64, [P("pipe", "M30 128 V136 H90 V128 M30 14 V6 H90 V14"), P("shell", TWIN),
    P("detail", "M14 40 H46 M14 100 H46 M74 40 H106 M74 100 H106"),
    P("detail", " ".join(f"M{x} {y} h0.1" for x in (20, 30, 40, 80, 90, 100) for y in (52, 64, 76, 88)), width=2.5)], desc="Twin-tower desiccant dryer / adsorber")
add("Membrane", PR, (100, 60), 48, [P("pipe", "M2 30 H10 M90 20 H98 M90 40 H98"), R("shell", 10, 10, 80, 40), P("detail", "M10 50 L90 10", dash="5 4", width=1.5)], desc="Membrane separator")
add("Centrifuge", PR, (100, 100), 48, [P("detail", "M50 4 V40", width=1.5), C("body", 50, 58, 34), P("detail", "M30 42 V68 Q50 84 70 68 V42")], desc="Centrifuge (body = running)")
add("Ejector", PR, (100, 60), 48, [P("pipe", "M0 30 H6 M94 30 H100 M45 37 V60"), P("body", "M6 22 H34 L52 26 L94 14 V46 L52 34 L34 38 H6 Z")], desc="Ejector / eductor (motive left, suction bottom)")
add("Flare_Stack", PR, (60, 140), 28, [P("pipe", "M2 132 H30"), R("shell", 24, 30, 12, 104), P("body", "M30 28 Q16 16 26 2 Q30 14 34 6 Q44 16 30 28 Z")], desc="Flare stack (body = flame lit)")
add("Scale_Weigh", PR, (100, 60), 48, [R("face", 10, 18, 80, 10), P("detail", "M20 28 L14 42 H26 Z M80 28 L74 42 H86 Z"), P("detail", "M6 46 H94", width=1.5)], desc="Scale / load cells")
add("Burner", PR, (100, 100), 40, [P("pipe", "M2 70 H40"), P("plain", "M40 60 H60 V80 H40 Z"), P("body", "M60 70 Q76 50 96 70 Q76 90 60 70 Z")], desc="Burner (body = flame)")

# =================================================================== INSTRUMENTS (ISA-5.1)
IN = "Instruments"
RECT = (10, 10, 80, 80)
DIAM = "M50 10 L90 50 L50 90 L10 50 Z"
HEX = "M28 12 H72 L94 50 L72 88 H28 L6 50 Z"
LINES = {"Field": [], "Panel": [P("detail", "M10 50 H90", width=1.5)],
         "Aux": [P("detail", "M10 47 H90 M10 53 H90", width=1.2)],
         "Behind": [P("detail", "M10 50 H90", dash="6 4", width=1.5)]}
LOC_DESC = {"Field": "field mounted", "Panel": "main control room, operator accessible",
            "Aux": "auxiliary location, operator accessible", "Behind": "not normally accessible (behind panel)"}
for loc, ln in LINES.items():
    suf = "" if loc == "Panel" else f"_{loc}"
    add(f"Instrument{'' if loc == 'Panel' else '_' + loc}" if loc != "Panel" else "Instrument_Panel", IN, (100, 100), 52,
        [C("face", 50, 50, 40)] + ln, desc=f"Discrete instrument, {LOC_DESC[loc]}")
    add(f"HMI{suf}", IN, (100, 100), 52, [R("face", *RECT), C("detail", 50, 50, 40)] + ln, desc=f"Shared display / DCS / HMI function, {LOC_DESC[loc]}")
    add(f"PLC{suf}", IN, (100, 100), 52, [R("face", *RECT), P("detail", DIAM)] + ln, desc=f"PLC function, {LOC_DESC[loc]}")
    add(f"Computer{suf}", IN, (100, 100), 52, [P("face", HEX)] + ln, desc=f"Computer function, {LOC_DESC[loc]}")
add("Interlock", IN, (100, 100), 52, [P("face", "M50 4 L96 50 L50 96 L4 50 Z")], desc="Interlock / binary logic (diamond)")
add("Interlock_Panel", IN, (100, 100), 52, [P("face", "M50 4 L96 50 L50 96 L4 50 Z"), P("detail", "M4 50 H96", width=1.5)], desc="Interlock logic in control room")
BUBBLES = [s.name for s in SYMS if s.cat == IN]

PE = [P("pipe", "M2 50 H30"), P("pipe", "M70 50 H98")]
add("FE_Orifice", IN, (100, 100), 36, [P("pipe", "M2 50 H44"), P("pipe", "M56 50 H98"), P("outline", "M44 28 V72 M56 28 V72"), P("detail", "M44 28 V16 M56 28 V16")], desc="Orifice plate with flange taps")
add("FE_Magnetic", IN, (100, 100), 36, PE + [R("face", 30, 32, 40, 36), P("detail", "M40 60 V40 L50 52 L60 40 V60", width=1.5)], desc="Magnetic flowmeter")
add("FE_Turbine", IN, (100, 100), 36, PE + [R("face", 30, 32, 40, 36), P("detail", "M40 40 L60 60 M60 40 L40 60"), C("dark", 50, 50, 3)], desc="Turbine flowmeter")
add("FE_Vortex", IN, (100, 100), 36, PE + [R("face", 30, 32, 40, 36), P("dark", "M36 42 L44 50 L36 58 Z"), P("detail", "M50 43 Q56 50 50 57 M58 43 Q64 50 58 57")], desc="Vortex flowmeter")
add("FE_Coriolis", IN, (100, 100), 36, [P("pipe", "M2 70 H24"), P("pipe", "M76 70 H98"), P("pipe", "M24 70 V34 Q24 18 40 18 H60 Q76 18 76 34 V70"), R("face", 40, 26, 20, 14)], desc="Coriolis mass flowmeter")
add("FE_Ultrasonic", IN, (100, 100), 36, PE + [R("face", 30, 32, 40, 36), P("detail", "M36 64 L64 36", dash="4 3", width=1.5), R("dark", 32, 62, 6, 6), R("dark", 62, 32, 6, 6)], desc="Ultrasonic flowmeter")
add("FE_Venturi", IN, (100, 100), 36, [P("face", "M6 34 H26 L42 44 H58 L94 30 V70 L58 56 H42 L26 66 H6 Z")], desc="Venturi tube")
add("FE_Rotameter", IN, (60, 100), 24, [P("pipe", "M30 92 V100"), P("pipe", "M30 8 V0"), P("face", "M18 8 H42 L36 92 H24 Z"), P("dark", "M25 56 H35 L32 63 H28 Z")], desc="Variable area flowmeter (rotameter)")
add("FE_ThermalMass", IN, (100, 100), 36, PE + [R("face", 30, 32, 40, 36), P("detail", "M36 50 Q43 38 50 50 T64 50", width=1.5), P("detail", "M50 32 V20 M44 20 H56")], desc="Thermal mass flowmeter")
add("FE_Pitot", IN, (100, 100), 36, [P("pipe", "M2 64 H98"), P("outline", "M50 14 V60 H66")], desc="Pitot / averaging pitot tube")
add("TE_Thermowell", IN, (100, 100), 36, [P("pipe", "M2 70 H98"), P("face", "M44 10 V64 Q50 76 56 64 V10")], desc="Thermowell / temperature element")
add("PI_Gauge", IN, (100, 100), 36, [P("pipe", "M10 92 H90"), P("detail", "M50 62 V92", width=1.5), C("face", 50, 36, 26), P("detail", "M50 36 L66 24", width=1.5), C("dark", 50, 36, 3)], desc="Local pressure gauge")
add("LG_Sight_Gauge", IN, (60, 120), 24, [P("pipe", "M38 26 H60 M38 94 H60"), R("face", 22, 18, 16, 84), P("detail", "M30 24 V96")], desc="Level gauge glass (taps right)")
add("LE_Radar", IN, (100, 100), 36, [R("face", 38, 6, 24, 18, 2), P("detail", "M44 24 L28 76 M56 24 L72 76", dash="5 4", width=1.5)], desc="Radar level element (non-contact)")
add("LE_GuidedWave", IN, (100, 100), 36, [R("face", 38, 6, 24, 18, 2), P("detail", "M50 24 V92", width=2), C("dark", 50, 92, 3)], desc="Guided-wave radar / probe level element")
add("AE_Probe", IN, (100, 100), 36, [P("pipe", "M2 70 H98"), P("detail", "M50 14 V66", width=1.5), C("face", 50, 66, 6)], desc="Analyzer probe / sample element")

# =================================================================== FITTINGS  (static)
FT = "Fittings"
FP = lambda a=46, b=54: [P("pipe", f"M2 50 H{a}"), P("pipe", f"M{b} 50 H98")]
add("Flow_Arrow", FT, (100, 100), 36, [P("pipe", "M2 50 H98"), P("dark", "M38 36 L66 50 L38 64 Z")], desc="Flow direction arrow")
add("Reducer", FT, (100, 100), 36, [P("pipe", "M0 50 H20 M80 50 H100"), P("plain", "M20 30 L80 40 V60 L20 70 Z")], desc="Concentric reducer")
add("Reducer_Eccentric", FT, (100, 100), 36, [P("pipe", "M0 50 H20 M80 58 H100"), P("plain", "M20 30 L80 46 V70 H20 Z")], desc="Eccentric reducer (flat bottom)")
add("Flange", FT, (100, 100), 36, FP() + [P("detail", "M46 30 V70 M54 30 V70", width=2)], desc="Flanged joint")
add("Blind_Flange", FT, (100, 100), 36, [P("pipe", "M2 50 H46"), P("detail", "M46 30 V70", width=2), R("dark", 52, 30, 7, 40)], desc="Blind flange")
add("Spectacle_Blind_Open", FT, (100, 100), 36, FP(38, 62) + [C("plain", 50, 50, 12), P("detail", "M50 38 V26"), C("dark", 50, 18, 8)], desc="Spectacle blind, open (ring in line)")
add("Spectacle_Blind_Closed", FT, (100, 100), 36, FP(38, 62) + [C("dark", 50, 50, 12), P("detail", "M50 38 V28"), C("plain", 50, 18, 9)], desc="Spectacle blind, closed (blank in line)")
add("Spool_Removable", FT, (100, 100), 36, FP(30, 70) + [P("detail", "M30 38 H70 V62 H30 Z", dash="5 3", width=1.5)], desc="Removable spool")
add("Union", FT, (100, 100), 36, FP(44, 56) + [P("detail", "M44 38 V62 M56 38 V62 M44 50 H56", width=1.5)], desc="Union")
add("Cap", FT, (100, 100), 36, [P("pipe", "M2 50 H62"), P("plain", "M62 34 Q84 50 62 66 Z")], desc="Pipe cap")
add("Plug_Bull", FT, (100, 100), 36, [P("pipe", "M2 50 H62"), P("dark", "M62 38 L82 50 L62 62 Z")], desc="Bull plug")
add("Hose_Flexible", FT, (100, 100), 36, [P("pipe", "M2 50 H20 Q27.5 34 35 50 T50 50 T65 50 T80 50 H98")], desc="Flexible hose")
add("Expansion_Joint", FT, (100, 100), 36, FP(30, 70) + [P("detail", "M30 34 V66 M70 34 V66 M30 50 L35 36 L40 64 L45 36 L50 64 L55 36 L60 64 L65 36 L70 50", width=1.5)], desc="Expansion joint / bellows")
add("Strainer_Y", FT, (100, 100), 36, [P("pipe", "M2 40 H98"), P("plain", "M42 40 L64 78 L78 70 L58 40 Z"), P("detail", "M52 44 L70 74", dash="4 3")], desc="Y-strainer")
add("Strainer_Basket", FT, (100, 100), 36, [P("pipe", "M2 40 H34 M66 40 H98"), P("plain", "M34 34 H66 V84 H34 Z"), P("detail", "M40 42 V78 H60 V42", dash="4 3")], desc="Basket strainer")
add("Steam_Trap", FT, (100, 100), 36, FP(32, 68) + [C("plain", 50, 50, 18), P("detail", "M41 42 H59 M50 42 V62", width=1.5)], desc="Steam trap")
add("Sight_Glass", FT, (100, 100), 36, FP(32, 68) + [C("plain", 50, 50, 18), C("detail", 50, 50, 10)], desc="In-line sight glass / flow indicator")
add("Flame_Arrestor", FT, (100, 100), 36, FP(32, 68) + [R("plain", 32, 32, 36, 36), P("detail", "M32 32 L68 68 M68 32 L32 68 M50 32 V68")], desc="Flame arrestor")
add("Rupture_Disk", FT, (100, 100), 36, FP(44, 56) + [P("detail", "M42 30 Q56 50 42 70 M50 30 Q64 50 50 70", width=1.5)], desc="Rupture disk")
add("Silencer", FT, (100, 100), 36, FP(28, 72) + [R("plain", 28, 34, 44, 32, 6), P("detail", "M34 50 Q38 42 42 50 T50 50 T58 50 T66 50")], desc="Silencer / muffler")
add("Restriction_Orifice", FT, (100, 100), 36, [P("pipe", "M2 50 H98"), P("detail", "M46 30 V44 M46 56 V70 M54 30 V44 M54 56 V70", width=2)], desc="Restriction orifice")
add("Sample_Point", FT, (100, 100), 36, [P("pipe", "M2 70 H98"), P("detail", "M50 70 V42", width=1.5), C("plain", 50, 34, 8), P("detail", "M50 26 V14 L44 8", width=1.5)], desc="Sample point / connection")
add("Drain_Funnel", FT, (100, 100), 36, [P("pipe", "M50 2 V50"), P("plain", "M30 54 H70 L56 72 V92 H44 V72 Z")], desc="Drain / tundish")
add("Vent", FT, (100, 100), 36, [P("pipe", "M50 98 V32 Q50 14 66 14 Q82 14 82 32 V42")], desc="Vent (goose-neck)")
add("Spray_Nozzle", FT, (100, 100), 36, [P("pipe", "M50 2 V40"), P("plain", "M40 40 H60 L50 56 Z"), P("detail", "M50 58 L32 92 M50 58 L50 94 M50 58 L68 92", dash="4 3")], desc="Spray nozzle")
add("Tee_Junction", FT, (100, 100), 36, [P("pipe", "M2 50 H98 M50 50 V98"), C("dark", 50, 50, 4)], desc="Tee / connected junction")
add("Line_Crossing", FT, (100, 100), 36, [P("pipe", "M50 2 V98"), P("pipe", "M2 50 H38 A12 12 0 0 1 62 50 H98")], desc="Unconnected line crossing (hop)")
add("Pipe_Break", FT, (100, 100), 36, [P("pipe", "M2 50 H40 M60 50 H98"), P("detail", "M40 38 Q46 50 40 62 M60 38 Q54 50 60 62", width=1.5)], desc="Pipe break")
add("Connector_OffPage_Out", FT, (120, 60), 72, [P("plain", "M4 8 H96 L116 30 L96 52 H4 Z")], desc="ISA off-page connector, flow leaving (label in parent)")
add("Connector_OffPage_In", FT, (120, 60), 72, [P("plain", "M24 8 H116 V52 H24 L4 30 Z")], desc="ISA off-page connector, flow entering (label in parent)")
add("Connector_Utility", FT, (60, 60), 28, [P("plain", "M30 6 L54 30 L30 54 L6 30 Z")], desc="Utility connection diamond (label in parent)")

# =================================================================== LINES (legend tiles, static)
LN = "Lines"
def line(name, elems, desc):
    add(name, LN, (100, 20), 80, elems, desc=desc)
line("Line_Process_Major", [P("pipe", "M2 10 H98", width=3)], "Major process line")
line("Line_Process", [P("pipe", "M2 10 H98")], "Process line")
line("Line_Process_Minor", [P("pipe", "M2 10 H98", width=1)], "Minor process line")
line("Line_Utility", [P("pipe", "M2 10 H98", width=1.5, color="utility")], "Utility line")
line("Line_Future", [P("pipe", "M2 10 H98", dash="12 6")], "Future / existing-by-others line")
line("Line_Heat_Traced", [P("pipe", "M2 9 H98"), P("detail", "M2 15 H98", dash="6 4")], "Heat-traced line")
line("Line_Jacketed", [P("pipe", "M2 6 H98 M2 14 H98", width=1.5)], "Jacketed line")
line("Line_Signal_Electric", [P("detail", "M2 10 H98", dash="7 4")], "Electrical signal")
line("Line_Signal_Pneumatic", [P("detail", "M2 10 H98 M22 15 L28 5 M26 15 L32 5 M47 15 L53 5 M51 15 L57 5 M72 15 L78 5 M76 15 L82 5")], "Pneumatic signal")
line("Line_Signal_Hydraulic", [P("detail", "M2 10 H98 M25 10 V3 H31 M50 10 V3 H56 M75 10 V3 H81")], "Hydraulic signal")
line("Line_Capillary", [P("detail", "M2 10 H98 M22 5 L30 15 M30 5 L22 15 M47 5 L55 15 M55 5 L47 15 M72 5 L80 15 M80 5 L72 15")], "Filled system / capillary tube")
line("Line_Data_Link", [P("detail", "M2 10 H22 M30 10 H47 M55 10 H72 M80 10 H98"), C("detail", 26, 10, 4), C("detail", 51, 10, 4), C("detail", 76, 10, 4)], "Data / communication link")
line("Line_Wireless", [P("detail", "M2 10 Q8 2 14 10 T26 10 T38 10 T50 10 T62 10 T74 10 T86 10 T98 10")], "Wireless / guided EM signal")
line("Line_Mechanical", [P("detail", "M2 10 H98"), C("dark", 26, 10, 3), C("dark", 51, 10, 3), C("dark", 76, 10, 3)], "Mechanical link")

CATEGORIES = ["Rotating", "Valves", "Vessels", "HeatTransfer", "Process", "Instruments", "Fittings", "Lines"]
