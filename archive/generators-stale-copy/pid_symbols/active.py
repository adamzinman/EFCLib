"""
Active (controlled-device) symbols for PID_Symbols v3.
Geometry: reference library (claude.ai artifact 3BqrQ3x6MxzorkGYA2aoZz) + notes 5, 8, 13, 14.
Colors: EFC_Styles palette, revised to ISA-101 / ISA-18.2 / NFPA 79 / ANSI Z535 (notes 7, 10-12).

Roles
  state    fill = state color, stroke = alarm color/weight
  body     fill = neutral body, stroke = alarm
  head     fill = command color (actuator), stroke = alarm
  detail   thin dark line, static
  solid    dark fill, static
  cstroke  contrast line: dark normally, light when the body is dark (fault)
  cfill    contrast fill: same rule as cstroke
  pipe     nozzle / port stub, static
"""

PAL = {
    "running": "#FFFFFF", "stopped": "#9E9E9E", "transition": "#D9D9D9", "fault": "#3A3A3A",
    "body": "#EBEBEB", "outline": "#262626", "detail": "#262626", "pipe": "#333333",
    "con_dark": "#262626", "con_light": "#F2F2F2",
    "alarm": {1: "#00A3E0", 2: "#FFD200", 3: "#FF7A00", 4: "#D50000"},   # Low, Medium, High, Critical
    "fault_border": "#D50000",
}
W_OUTLINE, W_ALARM, W_DETAIL, W_CON, W_PIPE = 1.5, 3.0, 1.0, 1.5, 2.0

BOW = "M10,54 L10,86 L50,70 Z M90,54 L90,86 L50,70 Z"   # closed bowtie, vertical ends, centerline y=70

class Sym:
    def __init__(self, name, cat, vb, scale, elems, title, ports, kind, badge_i="top"):
        self.name, self.cat, self.vb, self.scale, self.elems = name, cat, vb, scale, elems
        self.title, self.ports, self.kind, self.badge_i = title, ports, kind, badge_i
    @property
    def size(self): return round(self.vb[0] * self.scale), round(self.vb[1] * self.scale)
    @property
    def k(self): return 1 / self.scale          # viewBox units per screen px
    @property
    def roles(self): return {e[1] for e in self.elems}

def P(role, d, **kw): return ("path", role, {"d": d}, kw)
def C(role, cx, cy, r, **kw): return ("circle", role, {"cx": cx, "cy": cy, "r": r}, kw)
def R(role, x, y, w, h, **kw): return ("rect", role, {"x": x, "y": y, "width": w, "height": h}, kw)

BASE = P("body", "M32,80 L68,80 L78,94 L22,94 Z")
SYMS = [
    # ---- Rotating (kind = "motor": start/stop template)
    Sym("Pump_Centrifugal", "Rotating", (100, 100), 0.56,
        [P("pipe", "M2,52 L22,52 M92,30 L98,30"), BASE, P("state", "M50,24 L92,24 L92,36 L72.98,36 A28,28 0 1 1 50,24 Z"), C("cfill", 50, 52, 6)],
        "Centrifugal pump", "Suction left (2,52); discharge top-right (98,30)", "motor", badge_i="low"),
    Sym("Pump_PD_Rotary", "Rotating", (100, 100), 0.56,
        [R("state", 4, 44, 20, 16), R("state", 76, 44, 20, 16), C("state", 50, 52, 28), C("cstroke", 50, 42, 9), C("cstroke", 50, 62, 9), BASE],
        "Rotary PD / gear pump", "Suction left (4,52); discharge right (96,52)", "motor"),
    Sym("Pump_Diaphragm", "Rotating", (100, 100), 0.56,
        [R("state", 4, 44, 20, 16), R("state", 76, 44, 20, 16), C("state", 50, 52, 28), P("cstroke", "M50,26 Q36,52 50,78"),
         P("cstroke", "M58,42 L66,52 L58,62"), BASE],
        "Diaphragm / metering pump", "Suction left (4,52); discharge right (96,52)", "motor"),
    Sym("Pump_Reciprocating", "Rotating", (120, 100), 0.5,
        [P("detail", "M70,50 L92,50"), C("body", 98, 50, 12), R("state", 10, 30, 60, 40), R("cfill", 36, 34, 6, 32),
         P("body", "M16,70 L64,70 L70,86 L10,86 Z")],
        "Reciprocating pump", "Suction/discharge on cylinder end (x=10)", "motor"),
    Sym("Compressor_Centrifugal", "Rotating", (100, 100), 0.64,
        [P("state", "M14,18 L86,34 L86,66 L14,82 Z"), P("cstroke", "M30,50 L70,50")],
        "Centrifugal compressor", "Suction left (14,50); discharge right (86,50)", "motor"),
    Sym("Compressor_Diaphragm", "Rotating", (100, 100), 0.64,
        [P("pipe", "M6,50 L12,50 M88,50 L94,50"), C("state", 50, 50, 38), P("cstroke", "M19,28 L87,40 M19,72 L87,60", w=1.0)],
        "Diaphragm compressor", "Suction left (6,50); discharge right (94,50)", "motor"),
    Sym("Pump_Vacuum", "Rotating", (100, 100), 0.64,
        [P("pipe", "M6,50 L12,50 M88,50 L94,50"), C("state", 50, 50, 38), P("cstroke", "M19,28 L87,40 M19,72 L87,60", w=1.0),
         C("cstroke", 33, 50, 7, w=1.5)],
        "Vacuum pump", "Suction left (6,50); discharge right (94,50). Inner circle at x=33 (just under half way from center to left edge)", "motor"),
    Sym("Blower", "Rotating", (100, 100), 0.56,
        [P("state", "M50,20 L92,20 L92,32 L76.83,32 A30,30 0 1 1 50,20 Z"), P("cstroke", "M50,50 L50,28 M50,50 L69,61 M50,50 L31,61"), C("cfill", 50, 50, 4)],
        "Blower / fan", "Inlet at eye (50,50); discharge top-right (92,26)", "motor", badge_i="low"),
    Sym("Agitator", "Rotating", (100, 100), 0.5,
        [P("detail", "M50,34 L50,84"), P("detail", "M30,78 L70,90 M30,90 L70,78"), C("state", 50, 20, 14), P("cstroke", "M45.5,26 L45.5,14 L50,21.2 L54.5,14 L54.5,26")],
        "Agitator / mixer", "Place over vessel; no process line", "motor"),
    Sym("Motor", "Rotating", (100, 100), 0.4,
        [C("state", 50, 50, 34), P("cstroke", "M39.5,64 L39.5,36 L50,52.8 L60.5,36 L60.5,64")],
        "Electric motor", "Generic drive", "motor"),
    Sym("HX_AirCooled", "HeatTransfer", (140, 110), 0.6,
        [R("body", 10, 14, 120, 24), P("detail", "M18,26 L22,20 L30,32 L38,20 L46,32 L54,20 L62,32 L70,20 L78,32 L86,20 L94,32 L102,20 L110,32 L118,20"),
         P("detail", "M30,38 L46,54 M110,38 L94,54"), C("state", 70, 72, 18), P("cstroke", "M70,72 L70,56 M70,72 L84,80 M70,72 L56,80"),
         P("detail", "M70,90 L70,104 M60,104 L80,104")],
        "Air-cooled exchanger (fin fan)", "State = fan running; bundle ports at ends of bundle (y=26)", "motor"),
    Sym("Heater_Electric", "HeatTransfer", (120, 90), 0.6,
        [R("body", 10, 30, 100, 44), P("detail", "M18,52 L28,40 L38,64 L48,40 L58,64 L68,40 L78,64 L88,40 L98,64 L102,52"),
         P("detail", "M60,30 L60,24"), R("state", 44, 6, 32, 18)],
        "Electric heater", "State on terminal box = energized; process through shell (y=52)", "motor"),
    # ---- Valves (kind = "onoff" or "control")
    Sym("Valve_OnOff_Pneumatic", "Valves", (100, 100), 0.36,
        [P("detail", "M50,70 L50,32"), R("head", 30, 16, 40, 16), P("state", BOW)],
        "On/off valve, pneumatic (rectangular actuator)", "Pipe centerline y=70, ends x=10/90", "onoff"),
    Sym("Valve_Solenoid", "Valves", (100, 100), 0.36,
        [P("detail", "M50,70 L50,32"), R("head", 36, 12, 28, 22), P("detail", "M56,17 Q50,12.5 45,16 Q42,21 50,23 Q58,25 55,29.5 Q50,34 44,30"), P("state", BOW)],
        "Solenoid valve", "Pipe centerline y=70", "onoff"),
    Sym("Valve_MOV", "Valves", (100, 100), 0.36,
        [P("detail", "M50,70 L50,36"), C("head", 50, 22, 14), P("detail", "M45.5,28 L45.5,16 L50,23.2 L54.5,16 L54.5,28"), P("state", BOW)],
        "Motor-operated valve", "Pipe centerline y=70", "onoff"),
    Sym("Valve_Control", "Valves", (100, 100), 0.36,
        [P("detail", "M50,70 L50,32"), P("head", "M28,32 A22,16 0 0 1 72,32 Z"), P("state", BOW)],
        "Control valve (diaphragm)", "Head = command (output > 0); body = position feedback", "control"),
]
BY = {s.name: s for s in SYMS}

# ------------------------------------------------------------------ color logic (shared by SVG export + Perspective expressions)
def colors(sym, state=0, command=-1, alarm=0):
    sc = {0: PAL["stopped"], 1: PAL["running"], 2: PAL["transition"], 3: PAL["fault"]}.get(state, PAL["transition"])
    head = sc if command < 0 else (PAL["running"] if command == 1 else PAL["stopped"])
    line = PAL["fault_border"] if state == 3 else PAL["alarm"].get(alarm, PAL["outline"])   # note 31: red border when faulted
    con = PAL["con_light"] if state == 3 else PAL["con_dark"]
    lw = (W_ALARM if (alarm or state == 3) else W_OUTLINE) * sym.k
    dash = f"{round(4 * sym.k, 2)} {round(3 * sym.k, 2)}" if state == 2 else "none"           # note 28 (B): dashed outline while travelling
    return dict(state=sc, head=head, line=line, con=con, lw=lw, dash=dash)

def resolve(e, sym, c):
    t, role, g, kw = e
    k = sym.k
    if role == "state":   return c["state"], c["line"], c["lw"]
    if role == "body":    return PAL["body"], c["line"], c["lw"]
    if role == "head":    return c["head"], c["line"], c["lw"]
    if role == "detail":  return "none", PAL["detail"], kw.get("w", W_DETAIL) * k
    if role == "solid":   return PAL["outline"], "none", 0
    if role == "cstroke": return "none", c["con"], kw.get("w", W_CON) * k
    if role == "cfill":   return c["con"], "none", 0
    if role == "pipe":    return "none", PAL["pipe"], kw.get("w", W_PIPE) * k
    raise ValueError(role)

def svg(sym, state=0, command=-1, alarm=0, px=None):
    c = colors(sym, state, command, alarm)
    w, h = sym.size
    if px: w, h = px, round(px * sym.vb[1] / sym.vb[0], 2)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sym.vb[0]} {sym.vb[1]}" width="{w}" height="{h}">']
    for i, e in enumerate(sym.elems):
        t, role, g, kw = e
        f, s, sw = resolve(e, sym, c)
        a = " ".join(f'{k}="{v}"' for k, v in g.items())
        dash = f' stroke-dasharray="{c["dash"]}"' if role == "state" and c["dash"] != "none" else ""
        o.append(f'<{t} id="{role}{i}" {a} fill="{f}"' + (f' stroke="{s}" stroke-width="{round(sw, 3)}" stroke-linejoin="round"{dash}' if s != "none" else "") + "/>")
    o.append("</svg>")
    return "\n".join(o)
