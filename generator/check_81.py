"""Ignition 8.1 import check for PID_Symbols.zip and EFC_Styles.zip (static; no gateway needed)."""
import zipfile, json, re, sys
EXPR_81 = {"case", "if", "indexOf", "lastIndexOf", "len", "numberFormat", "substring", "coalesce", "isNull", "concat",
           "upper", "lower", "trim", "replace", "split", "stringFormat", "left", "right", "toInt", "toFloat", "toStr", "toBoolean",
           "isAlarmActiveFiltered", "coalesce", "abs", "min", "max", "round", "now", "dateFormat", "getBit", "switch", "try", "lookup", "forceQuality", "isGood"}
PAR = {"none"} | {f"x{a}Y{b}" for a in ("Min", "Mid", "Max") for b in ("Min", "Mid", "Max")}   # Drawing preserveAspectRatio enum (8.1)
ok = True
def fail(m):
    global ok; ok = False; print("FAIL", m)
def exprs(o):
    if isinstance(o, dict):
        if o.get("type") == "expr": yield o["config"]["expression"]
        for v in o.values(): yield from exprs(v)
    elif isinstance(o, list):
        for v in o: yield from exprs(v)
def walk(c):
    yield c
    for ch in c.get("children", []): yield from walk(ch)
for zp in sys.argv[1:]:
    z = zipfile.ZipFile(zp); names = z.namelist()
    if "project.json" not in names: fail(f"{zp}: project.json missing at zip root")
    pj = json.loads(z.read("project.json"))
    for k in ("title", "enabled", "inheritable", "parent"):
        if k not in pj: fail(f"{zp}: project.json lacks {k}")
    for n in names:
        if n.endswith("resource.json"):
            r = json.loads(z.read(n)); folder = n.rsplit("/", 1)[0]
            for f in r.get("files", []):
                if f"{folder}/{f}" not in names: fail(f"{n}: listed file {f} missing")
            if r.get("scope") != "G" or r.get("version") != 1: fail(f"{n}: scope/version")
        if n.endswith("style.json"):
            s = json.loads(z.read(n))
            if "style" not in s.get("base", {}): fail(f"{n}: base.style missing")
            for v in s.get("variants", []):
                if "pseudo" not in v or "style" not in v: fail(f"{n}: bad variant")
        if n.endswith("view.json"):
            v = json.loads(z.read(n))
            for e in exprs(v):
                for fn in re.findall(r"\b([a-zA-Z]+)\(", re.sub(r'"[^"]*"', "", e)):
                    if fn not in EXPR_81: fail(f"{n}: expression function {fn}() not in 8.1")
            for c in walk(v["root"]):
                if c.get("type") == "ia.shapes.svg" and c.get("props", {}).get("preserveAspectRatio", "xMidYMid") not in PAR:
                    fail(f"{n}: {c['meta']['name']} preserveAspectRatio not in 8.1 enum")
                if c.get("props", {}).get("mode") == "percent":
                    for ch in c.get("children", []):
                        p = ch.get("position", {})
                        for k in ("x", "y", "width", "height"):
                            if not (isinstance(p.get(k), (int, float)) and 0 <= p[k] <= 1): fail(f"{n}: {ch['meta']['name']} {k}={p.get(k)} not a 0-1 fraction")
    print(f"{zp}: {len(names)} entries checked")
print("PASS" if ok else "ISSUES FOUND")
