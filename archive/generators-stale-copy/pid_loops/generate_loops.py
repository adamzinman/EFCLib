"""Generate Perspective 8.1 PID loop templates (B1-B4), config popup, demo view, UDT + demo tags.

Writes projects/PID_Loops (project source) and tags/PID_Loops. Run tools/package.py to build the import zip."""
import json, os, shutil, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PROJ = os.path.join(ROOT, "projects", "PID_Loops")
TAGS = os.path.join(ROOT, "tags", "PID_Loops")
shutil.rmtree(PROJ, ignore_errors=True)
VIEWS = os.path.join(PROJ, "com.inductiveautomation.perspective", "views")

# ---------------------------------------------------------------- palette (ISA-101, matches the mockup)
C = dict(card="#F7F8F9", line="#C3C8CE", line2="#9AA1A9", txt="#1E2329", muted="#6B737C", sp="#2F6FD6",
         bar="#7C858F", bar2="#A9B0B8", track="#E6E9EC", band="#CBD2D9", chip="#E9ECEF", chipTxt="#454D55",
         dark="#2B3138", casBg="#DCE6F7", casTxt="#1F4E99", alH="#FF8C00", warnBg="#FFE7CC", warnTxt="#8A4A00",
         white="#FFFFFF", lockBg="#FFF7E0", lockTxt="#6A5300")
FONT = "Inter, 'Segoe UI', Roboto, Arial, sans-serif"
NUM = "tabular-nums"


def v(px):
    """1080p pixels -> vh so text/padding scale with the screen like the AutoValve template."""
    return "%gvh" % round(px / 10.8, 3)


# ---------------------------------------------------------------- binding helpers
def tag(path, bidir=False):
    cfg = {"fallbackDelay": 2.5, "mode": "indirect", "references": {"1": "{view.params.tagPath}"},
           "tagPath": "{1}/" + path}
    if bidir:
        cfg["bidirectional"] = True
    return {"binding": {"type": "tag", "config": cfg}}


def expr(e):
    return {"binding": {"type": "expr", "config": {"expression": e}}}


def prop(p, bidir=False):
    cfg = {"path": p}
    if bidir:
        cfg["bidirectional"] = True
    return {"binding": {"type": "property", "config": cfg}}


def indent(code):
    return "\n".join("\t" + ln if ln else "" for ln in code.strip("\n").split("\n"))


def with_script(binding, code):
    binding["binding"]["transforms"] = [{"type": "script", "code": indent(code)}]
    return binding


def ev(code):
    return {"type": "script", "scope": "G", "config": {"script": indent(code)}}


# ---------------------------------------------------------------- component helpers
def comp(type_, name, props=None, children=None, position=None, propConfig=None, events=None, custom=None):
    c = {"type": type_, "meta": {"name": name}, "props": props or {}}
    if position is not None:
        c["position"] = position
    if children is not None:
        c["children"] = children
    if propConfig:
        c["propConfig"] = propConfig
    if events:
        c["events"] = events
    if custom:
        c["custom"] = custom
    return c


def flex(name, direction, children, style=None, pos=None, justify=None, align=None, pc=None, events=None, wrap=None):
    p = {"direction": direction, "style": style or {}}
    if justify: p["justify"] = justify
    if align: p["alignItems"] = align
    if wrap: p["wrap"] = wrap
    return comp("ia.container.flex", name, p, children, pos or {"shrink": 0}, pc, events)


def label(name, text="", style=None, pos=None, pc=None):
    st = {"fontFamily": FONT, "color": C["txt"]}
    st.update(style or {})
    return comp("ia.display.label", name, {"text": text, "style": st}, None, pos or {"shrink": 0}, pc)


def drawing(name, viewBox, elements, pos, pc=None, par="xMidYMid"):
    return comp("ia.shapes.svg", name, {"viewBox": viewBox, "preserveAspectRatio": par, "elements": elements},
                None, pos, pc)


def rect(name, x, y, w, h, fill, rx=0):
    return {"type": "rect", "name": name, "x": x, "y": y, "width": w, "height": h, "rx": rx, "ry": rx,
            "fill": {"paint": fill}, "stroke": {"paint": "none", "width": 0}}


def path(name, d, fill="none", stroke="none", width=0, dash=None):
    s = {"paint": stroke, "width": width}
    if dash:
        s["dasharray"] = dash
    return {"type": "path", "name": name, "d": d, "fill": {"paint": fill}, "stroke": s}


# ---------------------------------------------------------------- shared custom props for the templates
def pct(x):
    return ("min(100, max(0, ({%s} - {view.custom.pvLo}) / max(0.000001, {view.custom.pvHi} - {view.custom.pvLo}) * 100))"
            % x)


FMT = '"#,##0.0"'
TEMPLATE_CUSTOM_PC = {
    "custom.pv": tag("PV"), "custom.sp": tag("SP"), "custom.out": tag("OUT"), "custom.mode": tag("Mode"),
    "custom.almHi": tag("AlmHi"), "custom.almLo": tag("AlmLo"),
    "custom.pvLo": tag("PV.engLow"), "custom.pvHi": tag("PV.engHigh"), "custom.units": tag("PV.engUnit"),
    "custom.pvPct": expr(pct("view.custom.pv")), "custom.spPct": expr(pct("view.custom.sp")),
    "custom.hiPct": expr(pct("view.custom.almHi")), "custom.loPct": expr(pct("view.custom.almLo")),
    "custom.outPct": expr("min(100, max(0, {view.custom.out}))"),
    "custom.alarm": expr("{view.custom.pv} >= {view.custom.almHi} || {view.custom.pv} <= {view.custom.almLo}"),
    "custom.modeText": expr('case({view.custom.mode}, 0, "MAN", 1, "AUTO", 2, "CAS", "---")'),
    "custom.name": expr('if(len({view.params.label}) > 0, {view.params.label}, '
                        'substring({view.params.tagPath}, lastIndexOf({view.params.tagPath}, "/") + 1))'),
    "params.tagPath": {"paramDirection": "input", "persistent": True},
    "params.label": {"paramDirection": "input", "persistent": True},
}
TEMPLATE_CUSTOM = {k.split(".", 1)[1]: 0 for k in TEMPLATE_CUSTOM_PC if k.startswith("custom.")}
TEMPLATE_CUSTOM.update(units="", modeText="", name="", alarm=False)

OPEN_POPUP = '''
tp = self.view.params.tagPath
system.perspective.openPopup("loopcfg_" + tp, "PID/Popups/LoopConfig", params={"tagPath": tp},
	title=self.view.custom.name, showCloseIcon=True, draggable=True, resizable=False, modal=False,
	overlayDismiss=True)
'''


def card_root(children, pad, extra_style=None, direction="column", align=None):
    st = {"backgroundColor": C["card"], "borderRadius": v(8), "boxShadow": "0 1px 2px rgba(20,30,40,0.08)",
          "padding": pad, "cursor": "pointer", "fontFamily": FONT, "overflow": "hidden"}
    st.update(extra_style or {})
    return flex("root", direction, children, st, None, align=align,
                pc={"props.style.border": expr('if({view.custom.alarm}, "2px solid %s", "1px solid %s")'
                                               % (C["alH"], C["line"]))},
                events={"dom": {"onClick": ev(OPEN_POPUP)}})


def diamond(size=11):
    return drawing("alarmIcon", "0 0 12 12", [path("d", "M6,0.8 L11.2,6 L6,11.2 L0.8,6 Z", C["alH"], "#222222", 0.8)],
                   {"shrink": 0, "basis": v(size)}, pc={"position.display": prop("view.custom.alarm")})


def tag_title(center=False):
    return flex("title", "row", [
        label("tag", "", {"fontWeight": 600, "fontSize": v(12.5), "whiteSpace": "nowrap"},
              pc={"props.text": prop("view.custom.name")}),
        diamond()], {"gap": v(5), "height": v(16)}, justify="center" if center else None, align="center")


def chip():
    return label("mode", "", {"fontSize": v(10), "fontWeight": 600, "letterSpacing": "0.04em", "padding": "%s %s" % (v(2), v(7)),
                              "borderRadius": "999px", "lineHeight": 1.2},
                 pc={"props.text": prop("view.custom.modeText"),
                     "props.style.backgroundColor": expr('case({view.custom.mode}, 0, "%s", 2, "%s", "%s")' % (C["dark"], C["casBg"], C["chip"])),
                     "props.style.color": expr('case({view.custom.mode}, 0, "%s", 2, "%s", "%s")' % (C["white"], C["casTxt"], C["chipTxt"]))})


def header():
    return flex("header", "row", [tag_title(), chip()], {"marginBottom": v(8)}, justify="space-between", align="center")


def num_label(name, prop_path, size, weight=600, color=None, extra=None, prefix=""):
    st = {"fontSize": v(size), "fontWeight": weight, "fontVariantNumeric": NUM, "lineHeight": 1}
    if color: st["color"] = color
    st.update(extra or {})
    e = 'numberFormat({%s}, %s)' % (prop_path, FMT)
    if prefix: e = '"%s" + %s' % (prefix, e)
    return label(name, "", st, pc={"props.text": expr(e)})


def small(name, text, extra=None):
    st = {"fontSize": v(10), "fontWeight": 600, "letterSpacing": "0.05em", "color": C["muted"]}
    st.update(extra or {})
    return label(name, text, st)


def units_label(name="units", size=10, extra=None):
    st = {"fontSize": v(size), "color": C["muted"]}
    st.update(extra or {})
    return label(name, "", st, pc={"props.text": prop("view.custom.units")})


def vbar(name, H, x0, w, basis, with_out=None):
    """Vertical PV bar with SP pointer and alarm ticks. viewBox height H."""
    W = x0 + w + 10
    els = [rect("track", x0, 0, w, H, C["track"], w / 2), rect("fill", x0, H, w, 0, C["bar"], w / 2),
           rect("hi", x0 + w + 2, 0, 5, 2, C["alH"], 1), rect("lo", x0 + w + 2, 0, 5, 2, C["alH"], 1),
           path("sp", "", C["sp"])]
    pc = {"props.elements[1].height": expr("%g * {view.custom.pvPct} / 100" % H),
          "props.elements[1].y": expr("%g - %g * {view.custom.pvPct} / 100" % (H, H)),
          "props.elements[2].y": expr("%g - %g * {view.custom.hiPct} / 100 - 1" % (H, H)),
          "props.elements[3].y": expr("%g - %g * {view.custom.loPct} / 100 - 1" % (H, H)),
          "props.elements[4].d": expr('"M%g," + (%g - %g*{view.custom.spPct}/100 - 5) + " L%g," + (%g - %g*{view.custom.spPct}/100)'
                                      ' + " L%g," + (%g - %g*{view.custom.spPct}/100 + 5) + " Z"'
                                      % (x0 - 9, H, H, x0 - 2, H, H, x0 - 9, H, H))}
    if with_out is not None:
        ox = with_out
        els += [rect("outTrack", ox, 0, w, H, C["track"], w / 2), rect("outFill", ox, H, w, 0, C["bar2"], w / 2)]
        pc["props.elements[5].height"] = expr("%g * {view.custom.outPct} / 100" % H)
        pc["props.elements[6].y"] = expr("%g - %g * {view.custom.outPct} / 100" % (H, H))
        pc["props.elements[6].height"] = expr("%g * {view.custom.outPct} / 100" % H)
        del pc["props.elements[5].height"]
        W = ox + w + 2
    return drawing(name, "0 0 %g %g" % (W, H + 0.0), els, {"shrink": 0, "basis": basis}, pc)


def hbar_out(name="outBar", h=6):
    return drawing(name, "0 0 200 %d" % h, [rect("track", 0, 0, 200, h, C["track"], h / 2),
                                           rect("fill", 0, 0, 0, h, C["bar"], h / 2)],
                   {"grow": 1, "shrink": 1, "basis": "0px"},
                   {"props.elements[1].width": expr("2 * {view.custom.outPct}")}, par="none")


def view_json(root, size, custom, pc, params):
    return {"custom": custom, "params": params, "propConfig": pc,
            "props": {"defaultSize": {"width": size[0], "height": size[1]}}, "root": root}


def template(root, size, extra_custom=None, extra_pc=None):
    custom = dict(TEMPLATE_CUSTOM)
    custom.update(extra_custom or {})
    pc = dict(TEMPLATE_CUSTOM_PC)
    pc.update(extra_pc or {})
    return view_json(root, size, custom, pc, {"tagPath": "[default]PID_Demo/TIC101", "label": ""})


# ================================================================= B1 – original bar card (150x156)
def b1():
    body = flex("body", "row", [
        vbar("pvBar", 88, 10, 12, v(30)),
        flex("vals", "column", [
            num_label("pv", "view.custom.pv", 20),
            units_label(extra={"marginTop": v(3)}),
            flex("spacer", "row", [], pos={"grow": 1, "basis": "0px"}),
            flex("spRow", "row", [small("spLbl", "SP", {"color": C["sp"], "marginRight": v(4)}),
                                  num_label("sp", "view.custom.sp", 16, 600, C["sp"])], align="baseline", justify="flex-end"),
        ], {"textAlign": "right"}, {"grow": 1, "basis": "0px"}, align="flex-end"),
    ], {"gap": v(8)}, {"grow": 1, "basis": "0px"})
    outrow = flex("outRow", "row", [small("outLbl", "OUT"),
                                    flex("outVal", "row", [num_label("out", "view.custom.out", 16),
                                                           label("pctU", "%", {"fontSize": v(12), "color": C["txt"], "fontWeight": 600, "marginLeft": v(3)})],
                                         align="baseline")],
                  {"margin": "%s 0 %s 0" % (v(10), v(4))}, justify="space-between", align="baseline")
    outbar = flex("outBarRow", "row", [hbar_out()], {"height": v(6)})
    root = card_root([header(), body, outrow, outbar], "%s %s %s %s" % (v(8), v(10), v(10), v(10)))
    return template(root, (150, 156))


# ================================================================= B2 – horizontal (260x92)
def b2():
    H = 26
    els = [rect("track", 0, 9, 200, 10, C["track"], 5), rect("band", 0, 9, 0, 10, C["band"]),
           rect("fill", 0, 9, 0, 10, C["bar"], 5), rect("lo", 0, 21, 2, 5, C["alH"], 1),
           rect("hi", 0, 21, 2, 5, C["alH"], 1), path("sp", "", C["sp"])]
    pc = {"props.elements[1].x": expr("2 * {view.custom.loPct}"),
          "props.elements[1].width": expr("2 * max(0, {view.custom.hiPct} - {view.custom.loPct})"),
          "props.elements[2].width": expr("2 * {view.custom.pvPct}"),
          "props.elements[3].x": expr("2 * {view.custom.loPct} - 1"),
          "props.elements[4].x": expr("2 * {view.custom.hiPct} - 1"),
          "props.elements[5].d": expr('"M" + (2*{view.custom.spPct} - 5) + ",0 L" + (2*{view.custom.spPct} + 5) + ",0 L" + (2*{view.custom.spPct}) + ",7 Z"')}
    bar = drawing("pvBar", "-6 -1 212 %d" % (H + 1), els, {"grow": 1, "shrink": 1, "basis": "0px"}, pc, par="none")
    vals = flex("vals", "column", [
        flex("pvRow", "row", [num_label("pv", "view.custom.pv", 20), units_label(extra={"marginLeft": v(3)})], align="baseline"),
        flex("spRow", "row", [small("spLbl", "SP", {"color": C["sp"], "marginRight": v(4)}),
                              num_label("sp", "view.custom.sp", 13, 600, C["sp"])], {"marginTop": v(5)}, align="baseline"),
    ], pos={"shrink": 0, "basis": v(100)})
    mid = flex("mid", "row", [vals, flex("barWrap", "row", [bar], {"height": v(28)}, {"grow": 1, "basis": "0px"}, align="center")],
               {"gap": v(10)}, {"grow": 1, "basis": "0px"}, align="center")
    outrow = flex("outRow", "row", [small("outLbl", "OUT"), flex("ob", "row", [hbar_out(h=5)], {"height": v(5)}, {"grow": 1, "basis": "0px"}),
                                    num_label("out", "view.custom.out", 12, 600, extra={"minWidth": v(46), "textAlign": "right"}),
                                    label("pctU", "%", {"fontSize": v(10.5), "color": C["muted"]})],
                  {"gap": v(8), "marginTop": v(6)}, align="center")
    root = card_root([header(), mid, outrow], "%s %s %s %s" % (v(8), v(12), v(10), v(12)))
    return template(root, (260, 92))


# ================================================================= B3 – bar + sparkline (172x184)
SPARK = '''
base = self.view.params.tagPath
W, H = 150.0, 34.0
empty = {"pv": "", "sp": ""}
if not base:
	return empty
try:
	ds = system.tag.queryTagHistory(paths=[base + "/PV", base + "/SP"], rangeMinutes=1, returnSize=40,
		aggregationMode="Average", returnFormat="Wide", ignoreBadQuality=True)
except:
	return empty
rows = []
for r in range(ds.getRowCount()):
	a, b = ds.getValueAt(r, 1), ds.getValueAt(r, 2)
	if a is not None and b is not None:
		rows.append((float(a), float(b)))
if len(rows) < 2:
	return empty
lo = min(min(p) for p in rows)
hi = max(max(p) for p in rows)
pad = max((hi - lo) * 0.15, 0.5)
lo, hi = lo - pad, hi + pad
def y(val):
	return H - 3 - (val - lo) / (hi - lo) * (H - 6)
step = W / (len(rows) - 1)
def mk(i):
	return " ".join(("M" if n == 0 else "L") + "%.1f,%.1f" % (n * step, y(p[i])) for n, p in enumerate(rows))
return {"pv": mk(0), "sp": mk(1)}
'''


def b3():
    devexpr = "{view.custom.pv} - {view.custom.sp}"
    vals = flex("vals", "column", [
        flex("pvRow", "row", [num_label("pv", "view.custom.pv", 20), units_label(extra={"marginLeft": v(3)})], align="baseline", justify="flex-end"),
        flex("spRow", "row", [small("spLbl", "SP", {"color": C["sp"], "marginRight": v(4)}),
                              num_label("sp", "view.custom.sp", 13, 600, C["sp"])], align="baseline", justify="flex-end"),
        label("dev", "", {"fontSize": v(10), "fontWeight": 600, "padding": "%s %s" % (v(1), v(6)), "borderRadius": "999px",
                          "fontVariantNumeric": NUM},
              pc={"props.text": expr('"Δ " + if(%s >= 0, "+", "−") + numberFormat(abs(%s), %s)' % (devexpr, devexpr, FMT)),
                  "props.style.backgroundColor": expr('if(abs(%s) > {view.custom.devAlm}, "%s", "%s")' % (devexpr, C["warnBg"], C["chip"])),
                  "props.style.color": expr('if(abs(%s) > {view.custom.devAlm}, "%s", "%s")' % (devexpr, C["warnTxt"], C["chipTxt"]))}),
    ], {"gap": v(4)}, {"grow": 1, "basis": "0px"}, justify="space-between", align="flex-end")
    body = flex("body", "row", [vbar("pvBar", 62, 10, 10, v(28)), vals], {"gap": v(8), "height": v(64)})
    spark = drawing("spark", "0 0 150 34", [rect("bg", 0, 0, 150, 34, C["white"], 4),
                                           path("sp", "", "none", C["sp"], 1.2, "4 3"),
                                           path("pv", "", "none", C["txt"], 1.5)],
                    {"shrink": 0, "basis": v(36)},
                    {"props.elements[1].d": prop("view.custom.spark.sp"), "props.elements[2].d": prop("view.custom.spark.pv")},
                    par="none")
    sparkWrap = flex("sparkWrap", "column", [spark], {"marginTop": v(8), "border": "1px solid #E3E6E9", "borderRadius": v(6), "overflow": "hidden"})
    outrow = flex("outRow", "row", [small("outLbl", "OUT"),
                                    flex("outVal", "row", [num_label("out", "view.custom.out", 12),
                                                           label("pctU", "%", {"fontSize": v(10), "color": C["muted"], "marginLeft": v(3)})], align="baseline")],
                  {"margin": "%s 0 %s 0" % (v(8), v(4))}, justify="space-between", align="baseline")
    outbar = flex("outBarRow", "row", [hbar_out(h=5)], {"height": v(5)})
    root = card_root([header(), body, sparkWrap, outrow, outbar], "%s %s %s %s" % (v(8), v(10), v(10), v(10)))
    spark_b = with_script(expr("now(5000)"), SPARK)
    return template(root, (172, 184), {"devAlm": 10, "spark": {"pv": "", "sp": ""}},
                    {"custom.devAlm": tag("AlmDev"), "custom.spark": spark_b})


# ================================================================= B4 – slim twin-bar column (104x196)
def b4():
    kids = [tag_title(center=True),
            flex("chipRow", "row", [chip()], {"margin": "%s 0 %s 0" % (v(5), v(7))}, justify="center"),
            flex("pvRow", "row", [num_label("pv", "view.custom.pv", 19)], justify="center"),
            flex("uRow", "row", [units_label()], justify="center"),
            flex("spRow", "row", [num_label("sp", "view.custom.sp", 12, 500, C["sp"], prefix="SP ")],
                 {"margin": "%s 0 %s 0" % (v(3), v(8))}, justify="center"),
            flex("bars", "row", [vbar("bars", 82, 10, 12, v(48), with_out=34)], {"height": v(82)}, justify="center"),
            flex("labs", "row", [
                flex("pvL", "column", [small("l", "PV")], pos={"shrink": 0, "basis": v(36)}, align="center"),
                flex("outL", "column", [small("l", "OUT"),
                                        label("out", "", {"fontSize": v(10.5), "fontWeight": 500, "color": C["chipTxt"], "fontVariantNumeric": NUM},
                                              pc={"props.text": expr('numberFormat({view.custom.out}, %s) + "%%"' % FMT)})],
                     pos={"shrink": 0, "basis": v(40)}, align="center")],
                 {"marginTop": v(6)}, justify="center")]
    root = card_root(kids, "%s %s %s %s" % (v(8), v(8), v(10), v(8)), {"textAlign": "center"})
    return template(root, (104, 196))


# ================================================================= Popup: PID/Popups/LoopConfig (440x470)
EDIT_NAMES = ["Kp", "Ti", "Td", "Action", "SP_Lo", "SP_Hi", "OUT_Lo", "OUT_Hi", "AlmHi", "AlmLo", "AlmDev"]
LOAD = '''
base = self.view.params.tagPath
names = %s
vals = system.tag.readBlocking([base + "/" + n for n in names])
edit = {}
for n, q in zip(names, vals):
	edit[n] = q.value
self.view.custom.edit = edit
''' % repr(EDIT_NAMES)
APPLY = '''
if self.view.custom.isEngineer:
	base = self.view.params.tagPath
	names = %s
	edit = self.view.custom.edit
	system.tag.writeBlocking([base + "/" + n for n in names], [edit[n] for n in names])
system.perspective.closePopup("")
''' % repr(EDIT_NAMES)
TREND = '''
base = self.view.params.tagPath
W, H = 400.0, 84.0
empty = {"pv": "", "sp": "", "out": ""}
if not base:
	return empty
try:
	ds = system.tag.queryTagHistory(paths=[base + "/PV", base + "/SP", base + "/OUT"], rangeMinutes=5,
		returnSize=120, aggregationMode="Average", returnFormat="Wide", ignoreBadQuality=True)
except:
	return empty
lo = float(self.view.custom.pvLo)
hi = float(self.view.custom.pvHi)
if hi <= lo:
	hi = lo + 1
rows = []
for r in range(ds.getRowCount()):
	vals = [ds.getValueAt(r, c) for c in (1, 2, 3)]
	if None not in vals:
		rows.append([float(x) for x in vals])
if len(rows) < 2:
	return empty
step = W / (len(rows) - 1)
def mk(i, a, b):
	pts = []
	for n, p in enumerate(rows):
		f = max(0.0, min(1.0, (p[i] - a) / (b - a)))
		pts.append(("M" if n == 0 else "L") + "%.1f,%.1f" % (n * step, H - 4 - f * (H - 8)))
	return " ".join(pts)
return {"pv": mk(0, lo, hi), "sp": mk(1, lo, hi), "out": mk(2, 0.0, 100.0)}
'''


def btn(name, text, primary=False, pos=None, pc=None, events=None):
    st = {"fontFamily": FONT, "fontWeight": 600, "fontSize": v(12.5), "borderRadius": v(8),
          "border": "1px solid " + (C["dark"] if primary else C["line"]),
          "backgroundColor": C["dark"] if primary else C["white"], "color": C["white"] if primary else C["txt"],
          "padding": "%s %s" % (v(6), v(18))}
    return comp("ia.input.button", name, {"text": text, "style": st}, None, pos or {"shrink": 0}, pc, events)


def mode_btn(val, text):
    sel = "{view.custom.mode} = %d" % val
    return btn("mode" + text, text, pos={"grow": 1, "basis": "0px"},
               pc={"props.style.backgroundColor": expr('if(%s, "%s", "transparent")' % (sel, C["white"])),
                   "props.style.boxShadow": expr('if(%s, "0 1px 3px rgba(20,30,40,0.18)", "none")' % sel),
                   "props.style.border": expr('"none"'), "props.style.color": expr('if(%s, "%s", "%s")' % (sel, C["txt"], "#4A535C"))},
               events={"component": {"onActionPerformed": ev(
                   'system.tag.writeBlocking([self.view.params.tagPath + "/Mode"], [%d])' % val)}})


def numfield(name, pc, pos=None, size=13, extra=None):
    st = {"fontFamily": FONT, "fontSize": v(size), "fontVariantNumeric": NUM, "textAlign": "right", "borderRadius": v(8)}
    st.update(extra or {})
    return comp("ia.input.numeric-entry-field", name, {"value": 0, "format": "0,0.0[00]", "style": st},
                None, pos or {"shrink": 0, "basis": v(130)}, pc)


def kpi(name, title, inner, pc=None):
    return flex(name, "column", [small("t", title, {"marginBottom": v(4)})] + inner,
                {"backgroundColor": C["card"], "border": "1px solid #E3E6E9", "borderRadius": v(10), "padding": "%s %s" % (v(9), v(11))},
                {"grow": 1, "basis": "0px"}, pc=pc)


def form_row(lbl, field_name, unit, enabled=True, dropdown=False):
    pc = {"props.value": prop("view.custom.edit." + field_name, True),
          "props.enabled": prop("view.custom.isEngineer")}
    if dropdown:
        f = comp("ia.input.dropdown", field_name, {"options": [{"value": 0, "label": "Reverse"}, {"value": 1, "label": "Direct"}],
                                                   "value": 0, "style": {"fontFamily": FONT, "fontSize": v(13), "borderRadius": v(8)}},
                 None, {"shrink": 0, "basis": v(130)}, pc)
    else:
        f = numfield(field_name, pc)
    return flex("row_" + field_name, "row", [
        label("lbl", lbl, {"fontSize": v(12.5), "color": "#3A424A"}, {"grow": 1, "basis": "0px"}),
        f, label("u", unit, {"fontSize": v(11), "color": C["muted"]}, {"shrink": 0, "basis": v(40)})],
        {"gap": v(10), "height": v(34)}, align="center")


def section(text):
    return small("sec_" + text.replace(" ", ""), text, {"marginTop": v(6)})


def popup():
    U = "view.custom.units"
    header_ = flex("header", "row", [
        flex("titles", "column", [
            label("tag", "", {"fontSize": v(17), "fontWeight": 700},
                  pc={"props.text": expr('substring({view.params.tagPath}, lastIndexOf({view.params.tagPath}, "/") + 1)')}),
            label("desc", "", {"fontSize": v(12.5), "color": C["muted"]}, pc={"props.text": tag("Description")})],
            pos={"grow": 1, "basis": "0px"}),
        btn("close", "×", pos={"shrink": 0}, events={"component": {"onActionPerformed": ev('system.perspective.closePopup("")')}})],
        {"padding": "%s %s %s %s" % (v(16), v(18), v(8), v(18))}, align="flex-start")
    header_["children"][1]["props"]["style"].update({"backgroundColor": C["chip"], "border": "none", "padding": "%s %s" % (v(2), v(10)), "fontSize": v(18)})

    seg = flex("modes", "row", [mode_btn(0, "MAN"), mode_btn(1, "AUTO"), mode_btn(2, "CAS")],
               {"backgroundColor": C["chip"], "borderRadius": v(10), "padding": v(3), "gap": v(3), "marginBottom": v(14)})
    kpis = flex("kpis", "row", [
        kpi("kPV", "PV", [flex("r", "row", [num_label("pv", "view.custom.pv", 20), label("u", "", {"fontSize": v(11), "color": C["muted"], "marginLeft": v(3)},
                                                                                         pc={"props.text": prop(U)})], align="baseline")]),
        kpi("kSP", "SP", [flex("r", "row", [
            numfield("sp", {"props.value": tag("SP", True), "props.enabled": expr("{view.custom.mode} != 2")},
                     {"grow": 1, "basis": "0px"}, 18, {"color": C["sp"], "fontWeight": 600}),
            label("u", "", {"fontSize": v(11), "color": C["muted"], "marginLeft": v(4)}, pc={"props.text": prop(U)})], align="center")]),
        kpi("kOUT", "OUT", [flex("r", "row", [
            numfield("out", {"props.value": tag("OUT", True), "props.enabled": expr("{view.custom.mode} = 0")},
                     {"grow": 1, "basis": "0px"}, 18, {"fontWeight": 600}),
            label("u", "%", {"fontSize": v(11), "color": C["muted"], "marginLeft": v(4)})], align="center")]),
    ], {"gap": v(10), "marginBottom": v(12)})
    trend = drawing("trend", "0 0 400 84", [rect("bg", 0, 0, 400, 84, C["card"], 8),
                                           path("out", "", "none", C["bar2"], 1.2),
                                           path("sp", "", "none", C["sp"], 1.5, "5 4"),
                                           path("pv", "", "none", C["txt"], 1.8)],
                    {"shrink": 0, "basis": v(84)},
                    {"props.elements[1].d": prop("view.custom.trend.out"), "props.elements[2].d": prop("view.custom.trend.sp"),
                     "props.elements[3].d": prop("view.custom.trend.pv")}, par="none")
    legend = flex("legend", "row", [
        label("l1", "━ PV", {"fontSize": v(11), "color": C["txt"]}), label("l2", "━ SP", {"fontSize": v(11), "color": C["sp"]}),
        label("l3", "━ OUT", {"fontSize": v(11), "color": C["bar2"]}), label("l4", "last 5 min", {"fontSize": v(11), "color": C["muted"]})],
        {"gap": v(14), "marginTop": v(6)})
    note = label("note", "OUT can be written only in MAN. SP is locked in CAS (it comes from the primary loop).",
                 {"fontSize": v(11.5), "color": C["muted"], "marginTop": v(10), "whiteSpace": "normal"})
    pane_style = {"padding": "%s %s" % (v(16), v(18))}
    operate = flex("Operate", "column", [seg, kpis, trend, legend, note], pane_style, {"tabIndex": 0})

    lock = label("lock", "", {"fontSize": v(12), "borderRadius": v(8), "padding": "%s %s" % (v(8), v(10)), "marginBottom": v(10), "whiteSpace": "normal"},
                 pc={"props.text": expr('if({view.custom.isEngineer}, "Changes are written to the PLC when you press Apply.", '
                                        '"Read only. Log in with the " + {view.custom.engineerRole} + " role to change tuning.")'),
                     "props.style.backgroundColor": expr('if({view.custom.isEngineer}, "%s", "%s")' % (C["chip"], C["lockBg"])),
                     "props.style.color": expr('if({view.custom.isEngineer}, "%s", "%s")' % (C["chipTxt"], C["lockTxt"]))})
    tuning = flex("Tuning", "column", [lock,
                                       form_row("Kp (gain)", "Kp", ""), form_row("Ti (integral)", "Ti", "s"),
                                       form_row("Td (derivative)", "Td", "s"), form_row("Action", "Action", "", dropdown=True)],
                  pane_style, {"tabIndex": 1})
    limits = flex("Limits", "column", [
        section("SETPOINT LIMITS"), form_row("SP low", "SP_Lo", "EU"), form_row("SP high", "SP_Hi", "EU"),
        section("OUTPUT LIMITS"), form_row("OUT low", "OUT_Lo", "%"), form_row("OUT high", "OUT_Hi", "%"),
        section("ALARMS"), form_row("PV high", "AlmHi", "EU"), form_row("PV low", "AlmLo", "EU"),
        form_row("Deviation", "AlmDev", "± EU")], pane_style, {"tabIndex": 2})
    tabs = comp("ia.container.tab", "tabs", {"tabs": ["Operate", "Tuning", "Limits & Alarms"], "currentTabIndex": 0,
                                             "menuType": "modern", "tabSize": {"width": 120, "height": 34},
                                             "contentStyle": {"backgroundColor": C["white"]},
                                             "menuStyle": {"inactive": {"fontFamily": FONT, "color": C["muted"]},
                                                           "active": {"fontFamily": FONT, "fontWeight": 600, "color": C["txt"]}}},
                [operate, tuning, limits], {"grow": 1, "basis": "0px"})
    footer = flex("footer", "row", [
        btn("cancel", "Cancel", events={"component": {"onActionPerformed": ev('system.perspective.closePopup("")')}}),
        btn("apply", "Apply", True, events={"component": {"onActionPerformed": ev(APPLY)}})],
        {"gap": v(8), "padding": "%s %s %s %s" % (v(10), v(18), v(16), v(18))}, justify="flex-end")
    root = flex("root", "column", [header_, tabs, footer], {"backgroundColor": C["white"], "fontFamily": FONT}, None,
                events={"system": {"onStartup": ev(LOAD)}})
    custom = {"pv": 0, "mode": 0, "units": "", "pvLo": 0, "pvHi": 100, "engineerRole": "Engineer", "isEngineer": False,
              "edit": {n: 0 for n in EDIT_NAMES}, "trend": {"pv": "", "sp": "", "out": ""}}
    pc = {"custom.pv": tag("PV"), "custom.mode": tag("Mode"), "custom.units": tag("PV.engUnit"),
          "custom.pvLo": tag("PV.engLow"), "custom.pvHi": tag("PV.engHigh"),
          "custom.isEngineer": with_script(prop("session.props.auth.user.roles"),
                                           'return self.view.custom.engineerRole in (value or [])'),
          "custom.trend": with_script(expr("now(5000)"), TREND),
          "params.tagPath": {"paramDirection": "input", "persistent": True}}
    return view_json(root, (440, 480), custom, pc, {"tagPath": "[default]PID_Demo/TIC101"})


# ================================================================= Demo screen
def demo():
    kids, y = [], 20
    loops = ["TIC101", "PIC205", "FIC310"]
    specs = [("B1_Bar", 150, 156), ("B2_Horizontal", 260, 92), ("B3_Sparkline", 172, 184), ("B4_Column", 104, 196)]
    for vname, w, h in specs:
        kids.append(label("title_" + vname, "Loop_" + vname, {"fontSize": v(13), "fontWeight": 600, "color": "#3A424A"},
                          {"x": 20, "y": y, "width": 300, "height": 20}))
        y += 26
        for i, lp in enumerate(loops):
            kids.append(comp("ia.display.view", "%s_%s" % (vname, lp),
                             {"path": "PID/Templates/Loop_" + vname, "params": {"tagPath": "[default]PID_Demo/" + lp, "label": ""}},
                             None, {"x": 20 + i * (w + 24), "y": y, "width": w, "height": h}))
        y += h + 24
    root = comp("ia.container.coord", "root", {"mode": "fixed", "style": {"backgroundColor": "#DADDE1"}}, kids)
    return view_json(root, (1000, y + 10), {}, {}, {})


# ================================================================= write project
def write_view(rel, data):
    d = os.path.join(VIEWS, *rel.split("/"))
    os.makedirs(d, exist_ok=True)
    json.dump(data, open(os.path.join(d, "view.json"), "w"), indent=2, ensure_ascii=False)
    json.dump({"scope": "G", "version": 1, "restricted": False, "overridable": True, "files": ["view.json"], "attributes": {"lastModification": {"actor": "admin", "timestamp": "2026-10-05T12:00:00Z"}}},
              open(os.path.join(d, "resource.json"), "w"), indent=2)


write_view("PID/Templates/Loop_B1_Bar", b1())
write_view("PID/Templates/Loop_B2_Horizontal", b2())
write_view("PID/Templates/Loop_B3_Sparkline", b3())
write_view("PID/Templates/Loop_B4_Column", b4())
write_view("PID/Popups/LoopConfig", popup())
write_view("PID/_Demo_Loops", demo())
json.dump({"title": "PID_Loops", "description": "PID loop templates B1-B4 + LoopConfig popup", "parent": "",
           "enabled": True, "inheritable": True}, open(os.path.join(PROJ, "project.json"), "w"), indent=2)

# ================================================================= tags
def mem(name, dt, value, **kw):
    t = {"name": name, "tagType": "AtomicTag", "valueSource": "memory", "dataType": dt, "value": value}
    t.update(kw)
    return t


udt = {"name": "PID_Loop", "tagType": "UdtType", "tags": [
    mem("PV", "Float4", 0.0, engUnit="EU", engLow=0.0, engHigh=100.0, formatString="#,##0.0",
        alarms=[{"name": "PV_High", "mode": "AboveValue", "priority": "High", "setpointA": {"bindType": "Tag", "value": "[.]AlmHi"}},
                {"name": "PV_Low", "mode": "BelowValue", "priority": "High", "setpointA": {"bindType": "Tag", "value": "[.]AlmLo"}}]),
    mem("SP", "Float4", 0.0), mem("OUT", "Float4", 0.0, engUnit="%", engLow=0.0, engHigh=100.0),
    mem("Mode", "Int2", 1, documentation="0 = MAN, 1 = AUTO, 2 = CAS"),
    mem("Kp", "Float4", 1.0), mem("Ti", "Float4", 30.0, engUnit="s"), mem("Td", "Float4", 0.0, engUnit="s"),
    mem("Action", "Int2", 0, documentation="0 = Reverse, 1 = Direct"),
    mem("SP_Lo", "Float4", 0.0), mem("SP_Hi", "Float4", 100.0), mem("OUT_Lo", "Float4", 0.0), mem("OUT_Hi", "Float4", 100.0),
    mem("AlmHi", "Float4", 90.0), mem("AlmLo", "Float4", 10.0), mem("AlmDev", "Float4", 10.0),
    mem("Description", "String", ""),
]}


def inst(name, desc, unit, lo, hi, pv, sp, out, mode, ah, al, splo, sphi):
    return {"name": name, "tagType": "UdtInstance", "typeId": "PID_Loop", "tags": [
        {"name": "PV", "tagType": "AtomicTag", "value": pv, "engUnit": unit, "engLow": lo, "engHigh": hi},
        {"name": "SP", "tagType": "AtomicTag", "value": sp}, {"name": "OUT", "tagType": "AtomicTag", "value": out},
        {"name": "Mode", "tagType": "AtomicTag", "value": mode},
        {"name": "AlmHi", "tagType": "AtomicTag", "value": ah}, {"name": "AlmLo", "tagType": "AtomicTag", "value": al},
        {"name": "SP_Lo", "tagType": "AtomicTag", "value": splo}, {"name": "SP_Hi", "tagType": "AtomicTag", "value": sphi},
        {"name": "Description", "tagType": "AtomicTag", "value": desc}]}


instances = {"name": "PID_Demo", "tagType": "Folder", "tags": [
    inst("TIC101", "Reactor jacket temperature", "°F", 0.0, 200.0, 118.4, 120.0, 46.0, 1, 130.0, 40.0, 20.0, 150.0),
    inst("PIC205", "Compressor discharge pressure", "PSIG", 0.0, 300.0, 262.0, 210.0, 88.0, 0, 250.0, 150.0, 100.0, 260.0),
    inst("FIC310", "N2 feed flow", "SCFM", 0.0, 500.0, 296.0, 300.0, 63.0, 2, 350.0, 50.0, 0.0, 450.0)]}
os.makedirs(TAGS, exist_ok=True)
json.dump(udt, open(os.path.join(TAGS, "PID_Loop_UDT.json"), "w"), indent=2, ensure_ascii=False)
json.dump(instances, open(os.path.join(TAGS, "PID_Loop_Demo_Instances.json"), "w"), indent=2, ensure_ascii=False)

print("PID_Loops written to", PROJ)
