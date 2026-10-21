"""Browser preview of the v3 templates (mirrors the Perspective expressions) + active symbols + static SVG library sheet."""
import os, html, re
from active import SYMS, BY, svg
from pid_common import LAYOUT, DEMO, UDTS, OUT

CSS = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build", "styles", "style_preview.html")).read().split("<style>")[1].split("</style>")[0]
CSS += """body{margin:0;padding:20px;background:#C8C8C8;font-family:Arial} h2{font:600 17px Arial;margin:18px 0 8px}
.row{display:flex;flex-wrap:wrap;gap:26px;background:#D9D9D9;padding:16px;border-radius:4px}
.t{position:relative;background:#D9D9D9}.a{position:absolute;display:flex;align-items:center;justify-content:center;box-sizing:border-box}
.line{position:absolute;height:2px;background:#333;left:-12px;right:-12px}
.mrow{display:flex;align-items:stretch;justify-content:center}.mrow>span{box-sizing:border-box;height:100%;display:flex;align-items:center}
figure{margin:0;display:grid;gap:6px;justify-items:center}figcaption{font:12px Arial;color:#333;text-align:center;max-width:280px}"""

def tagfmt(n): return re.sub(r'^([A-Z]+)', lambda m: m.group(1) + '-', n)

def box(b): x, y, w, h = b; return f"left:{x}px;top:{y}px;width:{w}px;height:{h}px"

def evaluate(udt, ov, tpl, p, name=""):
    t = {m["name"]: m["value"] for m in UDTS[udt]}; t.update(ov)
    t.setdefault("_P", not t.get("PermOK", True)); t.setdefault("_I", t.get("Intlk", False))
    t.setdefault("_L", "M" if t.get("Mode") == 1 else ""); t.setdefault("_EN", t.get("Cmd") or (t.get("PermOK", True) and not t.get("Intlk")))
    hasfb = p.get("hasFeedback", True)
    if tpl == "AutoValve":
        st = 3 if (t["ZSO"] and t["ZSC"]) else ((1 if t["CMD"] else 0) if not t["Feedback_Enabled"] else (1 if t["ZSO"] else 0 if t["ZSC"] else 2))
        cmd = (1 if t["CMD"] else 0) if t["Feedback_Enabled"] else -1
        status = {0: "CLOSED", 1: "OPEN", 2: "OPENING" if t["CMD"] else "CLOSING", 3: "FAULT"}[st]
        sym = BY[p.get("symbol", "Valve_OnOff_Pneumatic")]
        t["_P"], t["_I"] = t["Permissive"], t["Interlock"]
        t["_L"] = "L" if t["LockedOut"] else "D" if t["Off"] else "M" if t["Manual"] else ""
        t["_EN"] = t["Manual"] and not t["LockedOut"] and not t["Off"] and (t["CMD"] or (not t["Permissive"] and not t["Interlock"]))
        t["_TAG"] = t["Name"] or name
    elif tpl == "ControlValve":
        v = t["Pos"] if hasfb else t["Out"]
        st = 3 if t["Fault"] else (1 if v > 1 else 0); cmd = (1 if t["Out"] > 1 else 0) if hasfb else -1
        status = "FAULT" if st == 3 else f"{v:.0f} %"
        sym = BY[p.get("symbol", "Valve_Control")]
    else:
        st = 3 if t["Fault"] else ((1 if t["Cmd"] else 0) if not hasfb else (1 if t["Run"] and t["Cmd"] else 0 if not t["Run"] and not t["Cmd"] else 2))
        cmd = -1
        status = {0: "STOPPED", 1: "RUNNING", 2: "STARTING" if t["Cmd"] else "STOPPING", 3: "FAULT"}[st]
        sym = BY[p.get("symbol", "Rotating/Pump_Centrifugal").split("/")[-1]]
    return t, st, cmd, status, sym

def render(name, udt, ov, tpl, p, use_button=True):
    L = LAYOUT[tpl]; t, st, cmd, status, sym = evaluate(udt, ov, tpl, p, name)
    W, H = L["size"]; sx, sy, sw, sh = L["sym"]
    s = svg(sym, st, cmd, p.get("alarm", 0), px=sw)
    o = [f"<div class='t' style='width:{W}px;height:{H}px'>"]
    if sym.kind != "motor" or sym.name not in ("Agitator", "Motor"):
        o.append(f"<div class='line' style='top:{sy + L['line'] * sh - 1}px'></div>")
    o.append(f"<div class='a psc-Text_TagName' style='{box(L['tag'])}'>{t.get('_TAG') or tagfmt(name)}</div>")
    o.append(f"<div class='a' style='{box(L['sym'])}'>{s}</div>")
    if t["_P"]: o.append(f"<div class='a psc-Indicator_PermissiveBadge' style='{box(L['P'])}'>P</div>")
    if t["_I"]:
        ib = L["I_low"] if (tpl == "Motor" and sym.badge_i == "low") else L["I"]
        o.append(f"<div class='a psc-Indicator_InterlockBadge' style='{box(ib)}'>I</div>")
    letter = t["_L"]; man = bool(letter)
    if tpl == "Motor":
        cls = {0: "State_Stopped", 1: "State_Running", 2: "State_Transition", 3: "State_Fault"}[st]
        scls = f"psc-{cls}"
    else:
        scls = "psc-" + {0: "State_Stopped", 1: "State_Running", 2: "State_Transition", 3: "State_Fault"}[st]
    manual = (t.get("Manual") if tpl == "AutoValve" else t.get("Mode") == 1)
    showm = bool(manual and not use_button and tpl != "ControlValve")
    m = "<span class='a psc-Mode_ManualSplit' style='position:static'>M</span>" if showm else \
        ("<span class='a psc-Util_Collapsed' style='position:static'>M</span>" if tpl != "ControlValve" else "")   # mirrors Perspective: hidden M collapses to 0 width
    o.append(f"<div class='a mrow' style='{box(L['status'])}'>{m}<span class='a {scls}{' psc-Mode_ManualJoined' if showm else ''}' style='position:static'>{status}</span></div>")
    if tpl == "ControlValve" and "bar" in L:
        pos = max(0, min(100, t["Pos"])); out = max(0, min(100, t["Out"]))
        bar = (f"<svg viewBox='0 -6 20 112' preserveAspectRatio='none' width='{L['bar'][2]}' height='{L['bar'][3]}'>"
               f"<rect x='8' y='2' width='11' height='96' fill='#FFFFFF' stroke='#595959' stroke-width='1.5'/>"
               f"<rect x='8' y='{98-0.96*pos}' width='11' height='{0.96*pos}' fill='#4D4D4D'/>"
               f"<path d='M0 {91-0.96*out} L7 {98-0.96*out} L0 {105-0.96*out} Z' fill='#1F4E99'/></svg>")
        o.append(f"<div class='a' style='{box(L['bar'])}'>{bar}</div>")
    if use_button and L["pb"] and (t.get("Manual") if tpl == "AutoValve" else t.get("Mode") == 1):   # button only in Manual
        en = t["_EN"]
        o.append(f"<button class='a psc-Button_Command' {'' if en else 'disabled'} style='{box(L['pb'])}'></button>")
    o.append("</div>")
    return "".join(o)

def main():
    figs = []
    for n, u, ov, tpl, p in DEMO:
        desc = ", ".join(f"{k}={v}" for k, v in ov.items()) or "defaults"
        figs.append(f"<figure><div style='zoom:2.3'>{render(n, u, ov, tpl, p)}</div><figcaption><b>{tpl}</b> · {p.get('symbol', '')}<br>{desc}</figcaption></figure>")
    syms = []
    for s in SYMS:
        cells = "".join(f"<div style='display:grid;justify-items:center;font:11px Arial;color:#444'>{svg(s, st, -1, al, px=round(s.size[0] * 1.6))}<span>state {st}{' alarm ' + str(al) if al else ''}</span></div>"
                        for st, al in ((0, 0), (1, 0), (2, 0), (3, 0), (1, 3)))
        syms.append(f"<figure style='background:#D9D9D9;padding:8px;border:1px solid #BDBDBD'><div style='display:flex;gap:12px;align-items:flex-end'>{cells}</div><figcaption><b>{s.name}</b> · {s.title}</figcaption></figure>")
    page = (f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body>"
            f"<h2>Templates (demo tags) shown at 2.3x · dark line = process line</h2><div class=row>{''.join(figs)}</div>"
            f"<h2>Active symbols at 1.6x: stopped / running / transition / fault / running + high alarm</h2><div class=row>{''.join(syms)}</div></body></html>")
    open(os.path.join(OUT, "preview.html"), "w").write(page)

if __name__ == "__main__":
    main()
