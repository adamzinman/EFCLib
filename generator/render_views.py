#!/usr/bin/env python3
"""
Render every template in projects/EFC_Library to a PNG for design review (no gateway needed).

    python3 generator/render_views.py            # writes docs/previews/templates/<Category>/<Name>.png
                                                 # and docs/previews/review.html (contact sheet)

How it works: a small Perspective interpreter. Each view.json is read, its bindings are evaluated
against the demo tags in tags/ (tag, property and expression bindings, plus Jython script transforms
run as Python), and the components are drawn as HTML with the project's own style classes, then
screenshotted in headless Chromium (Playwright). Bindings it can't evaluate keep the value stored in
the view, which is what the Designer shows offline. It is a review aid, not a pixel-exact Perspective.
"""
import datetime, html, json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "projects", "EFC_Library", "com.inductiveautomation.perspective")
VIEWS = os.path.join(LIB, "views")
OUT = os.path.join(ROOT, "docs", "previews")

# ---------------------------------------------------------------- demo tags
def load_tags():
    types, roots = {}, []

    def collect_types(node):
        if node.get("tagType") == "UdtType":
            types[node["name"]] = node
        for ch in node.get("tags", []):
            collect_types(ch)

    for d, _, fs in os.walk(os.path.join(ROOT, "tags")):
        for f in fs:
            if f.endswith(".json"):
                doc = json.load(open(os.path.join(d, f), encoding="utf-8"))
                collect_types(doc)
                roots.append(doc)
    vals = {}

    def put(path, node):
        vals[path.lower()] = node.get("value")
        for k in ("engUnit", "engLow", "engHigh", "documentation", "tooltip", "formatString"):
            if k in node:
                vals[(path + "." + k).lower()] = node[k]

    def members(udt_name, prefix, inst_name, overrides):
        t = types.get(udt_name)
        if t:
            walk_members(t.get("tags", []), prefix, inst_name)
        walk_members(overrides, prefix, inst_name)

    def walk_members(tags, prefix, inst_name):
        for m in tags:
            p = prefix + "/" + m["name"]
            if m.get("tagType") == "UdtInstance":
                members(m.get("typeId", "").split("/")[-1], p, m["name"], m.get("tags", []))
            elif m.get("tagType") == "Folder":
                walk_members(m.get("tags", []), p, inst_name)
            else:
                if m.get("valueSource") == "expr" and "{InstanceName}" in m.get("expression", ""):
                    m = dict(m, value=inst_name)
                if "value" in m or (p.lower() not in vals):
                    put(p, m)

    def walk(node, prefix):
        tt = node.get("tagType")
        if tt == "UdtType" or node.get("name") == "_types_":
            return
        name = node.get("name")
        p = prefix + "/" + name if name else prefix
        if tt == "UdtInstance":
            members(node.get("typeId", "").split("/")[-1], p, name, node.get("tags", []))
        elif tt == "AtomicTag":
            put(p, node)
        for ch in node.get("tags", []) if tt in (None, "Folder", "Provider") else []:
            walk(ch, p)

    for r in roots:
        walk(r, "[default]")
    # "[default]/X" -> "[default]X"
    return {k.replace("[default]/", "[default]"): v for k, v in vals.items()}

TAGS = {}

# Preview-only fixture: the I/O faceplates ship without demo tags, so the renderer fakes one rack
# ([default]IO_Demo/Rack0) with the member names the faceplates read. Not an Ignition tag export.
IO_CARDS = [("R0S2", "BMXDDI1602", 2, 16, "16 DI, 24 VDC"), ("R0S3", "BMXDDO1602", 3, 16, "16 DO, 24 VDC"),
            ("R0S4", "BMXDDI3202K", 4, 32, "32 DI, 24 VDC"), ("R0S5", "BMXAMI0810", 5, 8, "8 AI, 4-20 mA"),
            ("R0S6", "BMXAMO0802", 6, 2, "2 AO, 4-20 mA"), ("R0S7", "BMXART0814", 7, 8, "8 TC/RTD"),
            ("R0S8", "BMXDDO3202K", 8, 32, "32 DO, 24 VDC"), ("R0S9", "BMXDDO6402K", 9, 64, "64 DO, 24 VDC")]
AI_DOC = [("PT-101", "N2 header pressure", "psig", 0, 300, 142.6), ("PT-102", "Ar header pressure", "psig", 0, 300, 118.2),
          ("FT-110", "Product flow", "slpm", 0, 500, 212.0), ("LT-120", "Dewar level", "%", 0, 100, 63.4),
          ("TT-130", "Cold box outlet", "°F", -320, 100, -297.5), ("PT-140", "Vacuum jacket", "inHgA", 0, 30, 0.4),
          ("AT-150", "O2 analyzer", "ppm", 0, 10, 1.8), (None, None, None, None, None, None)]

def io_fixture():
    t = {}
    def put(path, v):
        t[("[default]IO_Demo/Rack0/" + path).lower()] = v
    for folder, model, slot, n, desc in IO_CARDS:
        put(f"{folder}/CardModel", model); put(f"{folder}/Slot", slot); put(f"{folder}/Rack", 0)
        put(f"{folder}/CardDesc", desc); put(f"{folder}/Module/MOD_ERROR", False); put(f"{folder}/Module/HMI/DiagText", "")
        analog = model.startswith(("BMXAMI", "BMXAMO", "BMXART"))
        for ch in range(n):
            c = f"{folder}/CH{ch:02d}"
            if analog:
                if model == "BMXAMO0802":
                    doc = [("FCV-201", "Inlet control valve", "%", 0, 100, 46.0), ("PCV-202", "Back-pressure valve", "%", 0, 100, 18.5)][ch]
                elif model == "BMXART0814":
                    doc = [("TT-301", "Compressor 1st stage discharge", "°F", 0, 400, 212.4), ("TT-302", "Compressor 2nd stage discharge", "°F", 0, 400, 236.9),
                           ("TT-303", "Aftercooler outlet", "°F", 0, 200, 88.1), ("TT-304", "Oil sump", "°F", 0, 250, 131.0),
                           ("TT-305", "Motor winding A", "°F", 0, 350, 164.2), ("TT-306", "Motor winding B", "°F", 0, 350, 166.0),
                           (None, None, None, None, None, None), (None, None, None, None, None, None)][ch]
                else:
                    doc = AI_DOC[ch % len(AI_DOC)]
                loop, d, u, lo, hi, val = doc
                spare = loop is None
                put(f"{c}/Doc/LoopTag", loop or ""); put(f"{c}/Doc/Description", d or "Spare"); put(f"{c}/Doc/Spare", spare)
                put(f"{c}/Doc/Units", u or ""); put(f"{c}/Doc/EngMin", lo); put(f"{c}/Doc/EngMax", hi)
                put(f"{c}/HMI/Scaled", val); put(f"{c}/VALUE", None if spare else int(4000 + 16000 * ((val - lo) / (hi - lo)))
                    if lo is not None else 0)
                put(f"{c}/LOWER_LIMIT", False); put(f"{c}/UPPER_LIMIT", False)
                put(f"{c}/CH_ERROR", ch == 5 and model == "BMXAMI0810")
                put(f"{c}/HMI/DiagText", "Under range: open wire?" if ch == 5 and model == "BMXAMI0810" else "")
            else:
                spare = ch >= n - 3
                put(f"{c}/Doc/LoopTag", "" if spare else f"{'ZS' if 'DDI' in model else 'XV'}-{100 + ch}")
                put(f"{c}/Doc/Description", "Spare" if spare else ("Valve open limit" if "DDI" in model else "Solenoid"))
                put(f"{c}/Doc/Spare", spare); put(f"{c}/VALUE", (not spare) and ch % 3 != 1)
                put(f"{c}/CH_ERROR", False); put(f"{c}/HMI/DiagText", "")
    return t

def read_tag(path):
    if path is None:
        return None
    p = str(path).strip()
    if not p.startswith("["):
        p = "[default]" + p
    return TAGS.get(p.lower())

# ---------------------------------------------------------------- expression language
TOK = re.compile(r'\s*(?:(\d+\.\d*|\.\d+|\d+)|("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')|(\{[^}]*\})|(&&|\|\||==|!=|<=|>=|[-+*/%<>=!(),&|])|([A-Za-z_][\w.]*))')

class ExprError(Exception):
    pass

def tokenize(s):
    pos, out = 0, []
    while pos < len(s):
        if s[pos:].strip() == "":
            break
        m = TOK.match(s, pos)
        if not m:
            raise ExprError("bad token at " + s[pos:pos + 20])
        pos = m.end()
        num, st, ref, op, name = m.groups()
        if num is not None:
            out.append(("num", float(num) if "." in num else int(num)))
        elif st is not None:
            out.append(("str", bytes(st[1:-1], "utf-8").decode("unicode_escape") if "\\" in st else st[1:-1]))
        elif ref is not None:
            out.append(("ref", ref[1:-1]))
        elif op is not None:
            out.append(("op", op))
        else:
            out.append(("name", name))
    return out

PREC = {"||": 1, "&&": 2, "|": 3, "&": 3, "=": 4, "==": 4, "!=": 4, "<": 5, ">": 5, "<=": 5, ">=": 5,
        "+": 6, "-": 6, "*": 7, "/": 7, "%": 7}

def parse(tokens):
    i = [0]

    def peek():
        return tokens[i[0]] if i[0] < len(tokens) else (None, None)

    def take():
        t = peek(); i[0] += 1; return t

    def primary():
        k, v = take()
        if k == "num" or k == "str":
            return ("lit", v)
        if k == "ref":
            return ("ref", v)
        if k == "op" and v == "(":
            e = expr(0)
            if take() != ("op", ")"):
                raise ExprError(") expected")
            return e
        if k == "op" and v in ("!", "-"):
            return ("un", v, unary())
        if k == "name":
            if v in ("true", "false"):
                return ("lit", v == "true")
            if v == "null":
                return ("lit", None)
            if peek() == ("op", "("):
                take(); args = []
                if peek() != ("op", ")"):
                    while True:
                        args.append(expr(0))
                        if peek() == ("op", ","):
                            take(); continue
                        break
                if take() != ("op", ")"):
                    raise ExprError(") expected after args")
                return ("call", v, args)
        raise ExprError(f"unexpected {k} {v}")

    def unary():
        return primary()

    def expr(minp):
        left = primary()
        while True:
            k, v = peek()
            if k != "op" or v not in PREC or PREC[v] <= minp - 1 or PREC[v] < minp:
                break
            take()
            right = expr(PREC[v] + 1)
            left = ("bin", v, left, right)
        return left

    e = expr(0)
    if i[0] != len(tokens):
        raise ExprError("trailing tokens")
    return e

def truthy(v):
    if v is None:
        return False
    if isinstance(v, str):
        return v.strip().lower() in ("true", "1", "on", "yes")
    return bool(v)

def num(v):
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    try:
        return float(v)
    except Exception:
        raise ExprError("not a number")

def tostr(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float) and v.is_integer() and abs(v) < 1e15:
        return repr(v)
    return str(v)

def number_format(v, pat):
    try:
        x = float(num(v))
    except ExprError:
        return tostr(v)
    pat = pat.split(";")[0]
    dec = pat.split(".")[1] if "." in pat else ""
    mind = dec.count("0"); maxd = len([c for c in dec if c in "0#"])
    s = f"{x:,.{maxd}f}" if "," in pat else f"{x:.{maxd}f}"
    if maxd > mind and "." in s:
        intp, frac = s.split(".")
        frac = frac.rstrip("0")
        frac = frac + "0" * (mind - len(frac)) if len(frac) < mind else frac
        s = intp + ("." + frac if frac else "")
    return s

def evaluate(node, ctx):
    t = node[0]
    if t == "lit":
        return node[1]
    if t == "ref":
        return ctx.resolve(node[1])
    if t == "un":
        v = evaluate(node[2], ctx)
        return (not truthy(v)) if node[1] == "!" else -num(v)
    if t == "bin":
        op = node[1]
        if op == "&&":
            return truthy(evaluate(node[2], ctx)) and truthy(evaluate(node[3], ctx))
        if op == "||":
            return truthy(evaluate(node[2], ctx)) or truthy(evaluate(node[3], ctx))
        a, b = evaluate(node[2], ctx), evaluate(node[3], ctx)
        if op == "+":
            if isinstance(a, str) or isinstance(b, str):
                return tostr(a) + tostr(b)
            return num(a) + num(b)
        if op in ("=", "=="):
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                return float(a) == float(b)
            if isinstance(a, str) != isinstance(b, str) and a is not None and b is not None:
                return tostr(a) == tostr(b)
            return a == b
        if op == "!=":
            return not evaluate(("bin", "=", node[2], node[3]), ctx)
        if op in ("<", ">", "<=", ">="):
            if a is None or b is None:
                return False
            if isinstance(a, str) and isinstance(b, str):
                x, y = a, b
            else:
                x, y = num(a), num(b)
            return {"<": x < y, ">": x > y, "<=": x <= y, ">=": x >= y}[op]
        if op == "-": return num(a) - num(b)
        if op == "*": return num(a) * num(b)
        if op == "/":
            d = num(b)
            if d == 0: raise ExprError("div0")
            return num(a) / d
        if op == "%":
            d = num(b)
            if d == 0: raise ExprError("mod0")
            return math.fmod(num(a), d) if isinstance(num(a), float) or isinstance(d, float) else num(a) % d
        if op == "&": return int(num(a)) & int(num(b))
        if op == "|": return int(num(a)) | int(num(b))
        raise ExprError("op " + op)
    if t == "call":
        f, args = node[1], node[2]
        E = lambda k: evaluate(args[k], ctx)
        if f == "if":
            return E(1) if truthy(E(0)) else E(2)
        if f == "try":
            try:
                return E(0)
            except Exception:
                return E(1)
        if f == "coalesce":
            for k in range(len(args)):
                v = E(k)
                if v is not None:
                    return v
            return None
        if f == "case":
            v = E(0); n = len(args)
            for k in range(1, n - 1, 2):
                if evaluate(("bin", "=", ("lit", v), args[k]), ctx):
                    return E(k + 1)
            return E(n - 1) if n % 2 == 0 else None
        if f == "switch":
            v = E(0); n = (len(args) - 2) // 2
            for k in range(n):
                if evaluate(("bin", "=", ("lit", v), args[1 + k]), ctx):
                    return E(1 + n + k)
            return E(len(args) - 1)
        vals = [E(k) for k in range(len(args))]
        if f == "isNull": return vals[0] is None
        if f == "isGood": return vals[0] is not None
        if f in ("forceQuality",): return vals[0]
        if f == "isAlarmActiveFiltered": return False
        if f == "toStr": return tostr(vals[0]) if vals[0] is not None else None
        if f == "toBoolean": return truthy(vals[0])
        if f == "toInt": return int(num(vals[0]))
        if f == "toFloat": return float(num(vals[0]))
        if f == "len": return len(tostr(vals[0]))
        if f == "lastIndexOf": return tostr(vals[0]).rfind(tostr(vals[1]))
        if f == "indexOf": return tostr(vals[0]).find(tostr(vals[1]))
        if f == "substring":
            s = tostr(vals[0]); a = int(num(vals[1]))
            return s[a:int(num(vals[2]))] if len(vals) > 2 else s[a:]
        if f == "upper": return tostr(vals[0]).upper()
        if f == "lower": return tostr(vals[0]).lower()
        if f == "trim": return tostr(vals[0]).strip()
        if f == "concat": return "".join(tostr(v) for v in vals)
        if f == "max": return max(num(v) for v in vals)
        if f == "min": return min(num(v) for v in vals)
        if f == "abs": return abs(num(vals[0]))
        if f == "round": return round(num(vals[0]), int(num(vals[1])) if len(vals) > 1 else 0)
        if f == "numberFormat": return number_format(vals[0], tostr(vals[1]))
        if f == "stringFormat":
            s = tostr(vals[0])
            for v in vals[1:]:
                s = re.sub(r"%[-0-9.]*[sdf]", lambda m: tostr(v), s, count=1)
            return s
        if f == "now": return datetime.datetime(2026, 10, 19, 9, 30)
        if f == "dateFormat": return "2026-10-19 09:30"
        if f == "getBit": return (int(num(vals[0])) >> int(num(vals[1]))) & 1
        raise ExprError("function " + f)
    raise ExprError("node " + t)

EXPR_CACHE = {}

def run_expr(src, ctx):
    if src not in EXPR_CACHE:
        EXPR_CACHE[src] = parse(tokenize(src))
    return evaluate(EXPR_CACHE[src], ctx)

# ---------------------------------------------------------------- property paths
PATH_TOK = re.compile(r"\.?([^.\[\]]+)|\[(\d+)\]")

def split_path(p):
    out = []
    for m in PATH_TOK.finditer(p):
        out.append(int(m.group(2)) if m.group(2) is not None else m.group(1))
    return out

def get_path(obj, parts):
    for k in parts:
        try:
            obj = obj[k]
        except Exception:
            return None
    return obj

def set_path(obj, parts, value):
    for idx, k in enumerate(parts[:-1]):
        nxt = parts[idx + 1]
        if isinstance(obj, list):
            while len(obj) <= k:
                obj.append({})
            if not isinstance(obj[k], (dict, list)):
                obj[k] = [] if isinstance(nxt, int) else {}
            obj = obj[k]
        else:
            if not isinstance(obj.get(k), (dict, list)):
                obj[k] = [] if isinstance(nxt, int) else {}
            obj = obj[k]
    last = parts[-1]
    if isinstance(obj, list):
        while len(obj) <= last:
            obj.append(None)
    obj[last] = value

class Ctx:
    def __init__(self, view, comp=None):
        self.view, self.comp = view, comp

    def resolve(self, ref):
        ref = ref.strip()
        parts = split_path(ref)
        if not parts:
            return None
        if parts[0] == "view":
            return get_path(self.view, parts[1:])
        if parts[0] == "this" and self.comp is not None:
            return get_path(self.comp, parts[1:])
        if parts[0] == "session":
            return {"props": {"device": {"type": "browser"}, "auth": {"user": {"userName": "reviewer"}}}}.get(parts[1]) and None
        return None

# ---------------------------------------------------------------- bindings
class Shim:
    """Stands in for `self` inside script transforms."""
    def __init__(self, view, comp):
        self.view = Obj({"params": view["params"], "custom": view["custom"]})
        self.props = Obj(comp.get("props", {}) if comp else {})
        self.custom = Obj(comp.get("custom", {}) if comp else {})

class Obj(dict):
    def __getattr__(self, k):
        v = self.get(k)
        return Obj(v) if isinstance(v, dict) else v

class System:
    class tag:
        @staticmethod
        def readBlocking(paths):
            return [Q(read_tag(p)) for p in paths]
        @staticmethod
        def browse(path, flt=None):
            pre = str(path).lower().rstrip("/") + "/"
            kids = sorted({k[len(pre):].split("/")[0] for k in TAGS if k.startswith(pre) and "/" in k[len(pre):]})
            base = str(path).rstrip("/")
            class R:
                def getResults(self_):
                    return [{"fullPath": base + "/" + IO_NAMES.get(k, k)} for k in kids]
            return R()
    class util:
        @staticmethod
        def getLogger(*a):
            class L:
                def info(self, *a): pass
                warn = error = debug = info
            return L()
    class perspective:
        pass
    class date:
        @staticmethod
        def now():
            return datetime.datetime(2026, 10, 19, 9, 30)

class Q:
    def __init__(self, v): self.value = v; self.quality = "Good"

def to_py(v):
    """Jython sees Java-ish mutable objects; plain dicts/lists are fine for our scripts."""
    if isinstance(v, dict):
        return Obj({k: to_py(x) for k, x in v.items()})
    if isinstance(v, list):
        return [to_py(x) for x in v]
    return v

def run_script(code, value, view, comp):
    body = "def transform(self, value, quality, timestamp):\n" + "\n".join(
        ("\t" + l if not l.startswith("\t") else l) for l in code.replace("\r\n", "\n").split("\n"))
    g = {"system": System, "basestring": str, "unicode": str, "long": int, "xrange": range, "__builtins__": __builtins__}
    exec(compile(body, "<transform>", "exec"), g)
    return g["transform"](Shim(view, comp), to_py(value), "Good", None)

def interp(template, refs, ctx):
    def sub(m):
        key = m.group(1)
        r = refs.get(key)
        if r is None:
            return m.group(0)
        if r.startswith("{") and r.endswith("}"):
            v = ctx.resolve(r[1:-1])
        else:
            v = ctx.resolve(r)
        return tostr(v)
    return re.sub(r"\{(\w+)\}", sub, template)

def eval_binding(b, ctx, view, comp, current):
    t, cfg = b["type"], b.get("config", {})
    if t == "property":
        v = ctx.resolve(cfg["path"])
    elif t == "expr":
        v = run_expr(cfg["expression"], ctx)
    elif t == "tag":
        mode = cfg.get("mode", "direct")
        tp = cfg.get("tagPath", "")
        if mode == "indirect":
            tp = interp(tp, cfg.get("references", {}), ctx)
        elif mode == "expression":
            tp = tostr(run_expr(tp, ctx))
        v = read_tag(tp)
    elif t == "expr-struct":
        v = {k: run_expr(e, ctx) for k, e in cfg.get("struct", {}).items()}
    else:
        raise ExprError("binding " + t)
    for tr in b.get("transforms", []):
        if tr["type"] == "script":
            v = run_script(tr["code"], v, view, comp)
        elif tr["type"] == "map":
            out = tr.get("fallback")
            for m in tr.get("mappings", []):
                if evaluate(("bin", "=", ("lit", v), ("lit", m["input"])), ctx):
                    out = m["output"]; break
            v = out
        elif tr["type"] == "format":
            v = number_format(v, tr.get("formatValue", "#,##0.##"))
        elif tr["type"] == "expression":
            v = run_expr(tr["expression"].replace("{value}", "{view.__value}"), _ValueCtx(ctx, v))
        else:
            raise ExprError("transform " + tr["type"])
    return v

class _ValueCtx(Ctx):
    def __init__(self, base, value):
        super().__init__(base.view, base.comp); self._v = value
    def resolve(self, ref):
        return self._v if ref.strip() == "view.__value" else super().resolve(ref)

STATS = {"ok": 0, "fail": 0}

def apply_bindings(propconfig, target, ctx, view, comp, prefixes):
    for key, pc in propconfig.items():
        b = pc.get("binding") if isinstance(pc, dict) else None
        if not b or not key.split(".")[0].split("[")[0] in prefixes:
            continue
        parts = split_path(key)
        cur = get_path(target, parts)
        try:
            v = eval_binding(b, ctx, view, comp, cur)
            if b["type"] == "tag" and v is None and cur is not None:
                continue            # tag not in the demo set: keep the stored value
            set_path(target, parts, v)
            STATS["ok"] += 1
        except Exception:
            STATS["fail"] += 1

# ---------------------------------------------------------------- styles
UNITLESS = {"opacity", "zIndex", "fontWeight", "flexGrow", "flexShrink", "lineHeight", "order", "zoom"}

def kebab(k):
    return re.sub(r"([A-Z])", lambda m: "-" + m.group(1).lower(), k)

def css_decls(style, skip=("classes",)):
    out = []
    for k, v in (style or {}).items():
        if k in skip or v is None or isinstance(v, (dict, list)):
            continue
        if isinstance(v, bool):
            v = str(v).lower()
        if isinstance(v, (int, float)) and k not in UNITLESS:
            v = f"{v}px"
        out.append(f"{kebab(k)}:{v}")
    return ";".join(out)

def class_attr(style):
    cls = (style or {}).get("classes") or ""
    if isinstance(cls, list):
        cls = " ".join(cls)
    return " ".join("psc-" + c for c in str(cls).split() if c)

def css_escape(name):
    return re.sub(r"([^\w-])", r"\\\1", name)

def build_stylesheet():
    rules = []
    sc = os.path.join(LIB, "style-classes")
    for d, _, fs in os.walk(sc):
        if "style.json" not in fs:
            continue
        name = os.path.relpath(d, sc).replace(os.sep, "/")
        sel = ".psc-" + css_escape(name)
        doc = json.load(open(os.path.join(d, "style.json"), encoding="utf-8"))
        base = (doc.get("base") or {}).get("style") or {}
        rules.append(f"{sel}{{{css_decls(base)}}}")
        for var in doc.get("variants", []):
            st = css_decls((var.get("style") or {}))
            for sel_part in var_selectors(var, sel):
                rules.append(f"{sel_part}{{{st}}}")
    ss = os.path.join(LIB, "stylesheet", "stylesheet.css")
    if os.path.exists(ss):
        rules.append(open(ss, encoding="utf-8").read())
    return "\n".join(rules)

def var_selectors(var, sel):
    kind, val = var.get("type"), var.get("value") or var.get("pseudo") or ""
    if kind in ("pseudo", "element-state", "interaction") and val:
        return [f"{sel}:{val}"]
    if kind == "animation":
        return []
    if kind == "media":
        return []
    return []

# ---------------------------------------------------------------- views
VIEW_CACHE = {}

def load_view(path):
    if path not in VIEW_CACHE:
        VIEW_CACHE[path] = json.load(open(os.path.join(VIEWS, path, "view.json"), encoding="utf-8"))
    return json.loads(json.dumps(VIEW_CACHE[path]))

def prepare_view(path, params):
    v = load_view(path)
    view = {"params": dict(v.get("params") or {}), "custom": v.get("custom") or {}, "props": v.get("props") or {}}
    for k, x in (params or {}).items():
        view["params"][k] = x
    pc = v.get("propConfig") or {}
    ctx = Ctx(view)
    for _ in range(3):                         # custom props may read each other
        apply_bindings(pc, view, ctx, view, None, ("custom",))
    return v, view

def bind_component(c, view):
    ctx = Ctx(view, c)
    pc = c.get("propConfig") or {}
    for _ in range(2):
        apply_bindings(pc, c, ctx, view, c, ("custom", "props", "position", "meta"))

DEPTH = [0]

def render_view(path, params, w=None, h=None):
    if DEPTH[0] > 6 or not os.path.exists(os.path.join(VIEWS, path, "view.json")):
        return f"<div class='missing'>{html.escape(path)}</div>"
    DEPTH[0] += 1
    try:
        v, view = prepare_view(path, params)
        ds = (v.get("props") or {}).get("defaultSize") or {}
        W = w if w is not None else ds.get("width", 300)
        H = h if h is not None else ds.get("height", 200)
        root = v["root"]
        sz = f"width:{W}px;height:{H}px;" if isinstance(W, (int, float)) else f"width:{W};height:{H};"
        return f"<div class='pview' style='{sz}position:relative;overflow:hidden'>{render_comp(root, view, root=True)}</div>"
    finally:
        DEPTH[0] -= 1

def flex_props(p):
    d = p.get("direction", "row")
    return (f"display:flex;flex-direction:{d};flex-wrap:{p.get('wrap', 'nowrap')};"
            f"justify-content:{p.get('justify', 'flex-start')};align-items:{p.get('alignItems', 'flex-start')};"
            f"align-content:{p.get('alignContent', 'flex-start')};")

def child_style(pos, parent_type, pmode="fixed"):
    pos = pos or {}
    if parent_type == "ia.container.coord":
        def u(v):
            if isinstance(v, str):
                return v
            return f"{v * 100}%" if pmode == "percent" else f"{v}px"
        s = f"position:absolute;left:{u(pos.get('x', 0))};top:{u(pos.get('y', 0))};width:{u(pos.get('width', 100))};height:{u(pos.get('height', 30))};"
        if pos.get("rotate", {}).get("angle"):
            s += f"transform:rotate({pos['rotate']['angle']});"
        return s
    if parent_type in ("ia.container.flex", "repeater"):
        b = pos.get("basis", "auto")
        if isinstance(b, (int, float)):
            b = f"{b}px"
        return f"flex:{pos.get('grow', 0)} {pos.get('shrink', 1)} {b};min-width:0;min-height:0;position:relative;"
    return "position:relative;"

def is_hidden(c):
    if (c.get("meta") or {}).get("visible") is False:
        return True
    if (c.get("position") or {}).get("display") is False:
        return True
    return False

def render_comp(c, view, root=False, parent_type=None, pmode="fixed"):
    bind_component(c, view)
    if is_hidden(c):
        return ""
    t = c.get("type", "")
    p = c.get("props") or {}
    style = p.get("style") or {}
    cls = class_attr(style)
    outer = "width:100%;height:100%;box-sizing:border-box;" if root else child_style(c.get("position"), parent_type, pmode) + "box-sizing:border-box;"
    inline = css_decls(style)
    kids = c.get("children") or []
    if t == "ia.container.flex":
        inner = "".join(render_comp(k, view, parent_type="ia.container.flex") for k in kids)
        return f"<div class='{cls}' style='{outer}{flex_props(p)}{inline}'>{inner}</div>"
    if t == "ia.container.coord":
        inner = "".join(render_comp(k, view, parent_type="ia.container.coord", pmode=p.get("mode", "fixed")) for k in kids)
        posn = "absolute" if parent_type == "ia.container.coord" else "relative"
        return f"<div class='{cls}' style='{outer}position:{posn};{inline}'>{inner}</div>"
    if t == "ia.container.tab":
        tabs = p.get("tabs") or [f"Tab {i+1}" for i in range(len(kids))]
        cur = p.get("currentTabIndex", 0)
        head = "".join(f"<span class='tab{' on' if i == cur else ''}'>{html.escape(str(x))}</span>" for i, x in enumerate(tabs))
        body = render_comp(kids[cur], view, parent_type="ia.container.flex") if kids and cur < len(kids) else ""
        return f"<div class='{cls}' style='{outer}display:flex;flex-direction:column;{inline}'><div class='tabs'>{head}</div><div style='flex:1;position:relative;display:flex'>{body}</div></div>"
    if t == "ia.display.label":
        txt = p.get("text")
        txt = "" if txt is None else tostr(txt)
        ts = css_decls(p.get("textStyle") or {})
        ta = (p.get("textStyle") or {}).get("textAlign") or style.get("textAlign") or "left"
        jc = {"center": "center", "right": "flex-end", "end": "flex-end"}.get(ta, "flex-start")
        av = {"top": "flex-start", "bottom": "flex-end"}.get(p.get("alignVertical", "center"), "center")
        return (f"<div class='lbl {cls}' style='{outer}display:flex;align-items:{av};justify-content:{jc};{inline}'>"
                f"<span style='flex:1 1 auto;text-align:{ta if (p.get('textStyle') or {}).get('textAlign') or style.get('textAlign') else 'inherit'};{ts};min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:pre'>{html.escape(txt)}</span></div>")
    if t == "ia.input.button":
        txt = tostr(p.get("text", "Button"))
        dis = " dis" if p.get("enabled") is False else ""
        prim = "" if cls else " pbtn"
        return f"<div class='btn{prim}{dis} {cls}' style='{outer}display:flex;align-items:center;justify-content:center;{inline}'><span>{html.escape(txt)}</span></div>"
    if t in ("ia.input.numeric-entry-field", "ia.input.text-field", "ia.input.dropdown", "ia.input.text-area"):
        val = p.get("value", p.get("text"))
        if t == "ia.input.dropdown":
            opts = {str(o.get("value")): o.get("label") for o in (p.get("options") or []) if isinstance(o, dict)}
            val = opts.get(str(val), val) if val is not None else p.get("placeholder", {}).get("text", "Select…") if isinstance(p.get("placeholder"), dict) else "Select…"
        if t == "ia.input.numeric-entry-field" and isinstance(val, (int, float)) and not isinstance(val, bool):
            fmt = str(p.get("format", "0,0.##"))
            frac = fmt.split(".", 1)[1] if "." in fmt else ""
            req = len(re.sub(r"\[.*?\]", "", frac).replace("#", ""))
            dec = len(frac.replace("[", "").replace("]", ""))
            val = f"{val:,.{dec}f}" if "," in fmt else f"{val:.{dec}f}"
            if dec > req and "." in val:
                ip, fp = val.split(".")
                fp = fp.rstrip("0").ljust(req, "0")
                val = ip + ("." + fp if fp else "")
        caret = "<span class='caret'>▾</span>" if t == "ia.input.dropdown" else ""
        return f"<div class='inp {cls}' style='{outer}{inline}'><span>{html.escape(tostr(val))}</span>{caret}</div>"
    if t == "ia.input.checkbox":
        on = truthy(p.get("selected"))
        return f"<div class='chk {cls}' style='{outer}display:flex;align-items:center;gap:6px;{inline}'><span class='box{' on' if on else ''}'></span><span>{html.escape(tostr(p.get('text', '')))}</span></div>"
    if t == "ia.display.view":
        path = p.get("path") or ""
        params = p.get("params") or {}
        ds = None
        if p.get("useDefaultViewWidth") or p.get("useDefaultViewHeight"):
            try:
                ds = (load_view(path).get("props") or {}).get("defaultSize") or {}
            except Exception:
                ds = {}
        w = f"{ds.get('width')}px" if ds and p.get("useDefaultViewWidth") else "100%"
        h = f"{ds.get('height')}px" if ds and p.get("useDefaultViewHeight") else "100%"
        extra = (f"width:{w};" if p.get("useDefaultViewWidth") else "") + (f"height:{h};" if p.get("useDefaultViewHeight") else "")
        return f"<div class='{cls}' style='{outer}{extra}{inline}'>{render_view(path, params, '100%', '100%')}</div>"
    if t == "ia.display.flex-repeater":
        path = p.get("path") or ""
        ep = p.get("elementPosition") or {}
        es = css_decls(p.get("elementStyle") or {})
        items = []
        try:
            rds = (load_view(path).get("props") or {}).get("defaultSize") or {}
        except Exception:
            rds = {}
        fixw = f"width:{rds['width']}px;flex-shrink:0;" if p.get("useDefaultViewWidth", True) and rds.get("width") else ""
        fixh = f"height:{rds['height']}px;flex-shrink:0;" if p.get("useDefaultViewHeight", True) and rds.get("height") else ""
        for inst in p.get("instances") or []:
            inst = dict(inst or {})
            ist = css_decls(inst.pop("instanceStyle", {}) or {})
            ipos = dict(ep); ipos.update(inst.pop("instancePosition", {}) or {})
            items.append(f"<div style='{child_style(ipos, 'repeater')}{fixw}{fixh}{es};{ist}'>{render_view(path, inst, '100%', '100%')}</div>")
        fp = flex_props({"direction": p.get("direction", "row"), "wrap": "wrap" if p.get("wrap") else "nowrap",
                         "justify": p.get("justify", "flex-start"), "alignItems": p.get("alignItems", "flex-start"),
                         "alignContent": p.get("alignContent", "flex-start")})
        return f"<div class='{cls}' style='{outer}{fp}{inline}'>{''.join(items)}</div>"
    if t == "ia.shapes.svg":
        return f"<div class='{cls}' style='{outer}{inline}'>{render_svg(p)}</div>"
    if t == "ia.display.icon":
        col = p.get("color") or "#4A4A4A"
        return f"<div class='{cls}' style='{outer}{inline}'><svg viewBox='0 0 24 24' width='100%' height='100%'><circle cx='12' cy='12' r='7' fill='none' stroke='{col}' stroke-width='2'/></svg></div>"
    if t == "ia.display.image":
        return f"<div class='img {cls}' style='{outer}{inline}'></div>"
    return f"<div class='unk {cls}' title='{html.escape(t)}' style='{outer}{inline}'></div>"

def paint(v):
    if isinstance(v, dict):
        return v.get("paint"), v.get("opacity"), v
    return v, None, {}

def svg_el(e):
    t = e.get("type")
    attrs = []
    fill, fop, _ = paint(e.get("fill"))
    stroke, sop, sd = paint(e.get("stroke"))
    if fill is not None: attrs.append(f"fill='{fill}'")
    if fop is not None: attrs.append(f"fill-opacity='{fop}'")
    if stroke is not None: attrs.append(f"stroke='{stroke}'")
    if sop is not None: attrs.append(f"stroke-opacity='{sop}'")
    for k, a in (("width", "stroke-width"), ("dasharray", "stroke-dasharray"), ("linecap", "stroke-linecap"), ("linejoin", "stroke-linejoin")):
        if sd.get(k) is not None: attrs.append(f"{a}='{sd[k]}'")
    st = e.get("style")
    if isinstance(st, dict):
        cls = class_attr(st)
        if cls: attrs.append(f"class='{cls}'")
        decl = css_decls(st)
        if decl: attrs.append(f"style='{decl}'")
    if e.get("transform"): attrs.append(f"transform='{e['transform']}'")
    if e.get("visibility") == "hidden": return ""
    for k in ("d", "x", "y", "width", "height", "rx", "ry", "cx", "cy", "r", "x1", "y1", "x2", "y2", "points", "opacity",
              "fill-rule", "text-anchor", "font-size", "font-weight", "dominant-baseline"):
        if e.get(k) is not None:
            attrs.append(f"{k}='{html.escape(str(e[k]), quote=True)}'")
    a = " ".join(attrs)
    if t == "group":
        return f"<g {a}>{''.join(svg_el(x) for x in e.get('elements', []))}</g>"
    if t == "text":
        return f"<text {a}>{html.escape(tostr(e.get('text', '')))}</text>"
    if t in ("path", "rect", "circle", "ellipse", "line", "polyline", "polygon"):
        return f"<{t} {a}/>"
    return ""

def render_svg(p):
    vb = p.get("viewBox") or "0 0 100 100"
    par = p.get("preserveAspectRatio") or "xMidYMid"
    return (f"<svg viewBox='{vb}' preserveAspectRatio='{par}' width='100%' height='100%' style='display:block;overflow:visible'>"
            f"{''.join(svg_el(e) for e in (p.get('elements') or []))}</svg>")

# ---------------------------------------------------------------- catalog
BASE_CSS = """
*{box-sizing:border-box} body{margin:0;background:#D4D4D4;font-family:'Noto Sans','Segoe UI',Arial,sans-serif;font-size:1.296vh;color:#1F1F1F}
.pview{background:transparent}
.btn{cursor:default;border-radius:3px;font-size:1.296vh;user-select:none}
.pbtn{background:#E6E6E6;border:1px solid #9E9E9E;color:#1F1F1F}
.btn.dis{opacity:.55}
.inp{display:flex;align-items:center;justify-content:space-between;background:#FFF;border:1px solid #9E9E9E;border-radius:2px;padding:0 6px;font-size:1.296vh}
.inp .caret{color:#6E6E6E;margin-left:6px}
.chk .box{width:14px;height:14px;border:1px solid #6E6E6E;background:#FFF;border-radius:2px;flex:none}.chk .box.on{background:#4A4A4A}
.tabs{display:flex;gap:2px;border-bottom:1px solid #9E9E9E}.tab{padding:4px 10px;background:#E0E0E0}.tab.on{background:#F2F2F2;font-weight:600}
.missing{outline:1px dashed #C00;color:#C00;font:11px Arial;padding:2px}
.unk{outline:1px dashed #888}
.img{background:repeating-linear-gradient(45deg,#ddd 0 6px,#ccc 6px 12px)}
#stage{display:inline-block;padding:0}
"""

def embedded_uses():
    """First params each template is embedded with, anywhere in the library (demo screens mostly)."""
    uses = {}
    for d, _, fs in os.walk(VIEWS):
        if "view.json" not in fs:
            continue
        v = json.load(open(os.path.join(d, "view.json"), encoding="utf-8"))
        def walk(c):
            p = c.get("props") or {}
            if c.get("type") == "ia.display.view" and p.get("path"):
                uses.setdefault(p["path"], []).append(p.get("params") or {})
            if c.get("type") == "ia.display.flex-repeater" and p.get("path"):
                for inst in p.get("instances") or []:
                    uses.setdefault(p["path"], []).append({k: x for k, x in (inst or {}).items() if not k.startswith("instance")})
            for ch in c.get("children") or []:
                walk(ch)
        walk(v["root"])
    return uses

# Templates shown on the review sheet: (group, view path, note). Parts and demo screens are listed after.
GROUPS = [
    ("Valves", "Templates/Valves/"),
    ("Rotating equipment", "Templates/Rotating/"),
    ("Heat transfer", "Templates/HeatTransfer/"),
    ("Process values", "Templates/ProcessValues/"),
    ("PID loops", "Templates/Loops/"),
    ("Station faceplates", "Templates/Station/"),
    ("x80 I/O card faceplates", "Templates/IO/"),
]

IO_NAMES = {}
PARAM_OVERRIDES = {f"Templates/IO/Faceplates/{m}": {"cardPath": f"[default]IO_Demo/Rack0/{f}"} for f, m, *_ in IO_CARDS}

def main():
    global TAGS
    from playwright.sync_api import sync_playwright
    TAGS = load_tags()
    TAGS.update(io_fixture())
    IO_NAMES.update({f.lower(): f for f, *_ in IO_CARDS})
    css = BASE_CSS + build_stylesheet()
    uses = embedded_uses()
    views = sorted(os.path.relpath(d, VIEWS).replace(os.sep, "/") for d, _, fs in os.walk(VIEWS) if "view.json" in fs)
    items = []
    for group, pre in GROUPS:
        for v in views:
            if not v.startswith(pre):
                continue
            rest = v[len(pre):]
            kind = "demo" if "/_Demo" in "/" + rest or rest.startswith("_Demo") else "part" if rest.startswith("Parts/") else "template"
            items.append((group, v, kind))
    items += [("Library", "Templates/_Demo", "demo"), ("Library", "Styles/_Catalog", "demo")]
    out_t = os.path.join(OUT, "templates")
    import shutil
    shutil.rmtree(out_t, ignore_errors=True)
    os.makedirs(out_t, exist_ok=True)
    meta = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
        for group, v, kind in items:
            params = dict((uses.get(v) or [{}])[0]); params.update(PARAM_OVERRIDES.get(v, {}))
            STATS["ok"] = STATS["fail"] = 0
            body = render_view(v, params)
            doc = f"<html><head><meta charset='utf-8'><style>{css}</style></head><body><div id='stage'>{body}</div></body></html>"
            pg.set_content(doc)
            pg.wait_for_timeout(30)
            png = os.path.join(out_t, *v.replace("Templates/", "", 1).split("/")) + ".png"
            os.makedirs(os.path.dirname(png), exist_ok=True)
            pg.locator("#stage").screenshot(path=png, animations="disabled")
            ds = (load_view(v).get("props") or {}).get("defaultSize") or {}
            meta.append({"group": group, "path": v, "kind": kind, "png": os.path.relpath(png, OUT).replace(os.sep, "/"),
                         "size": f"{ds.get('width')}×{ds.get('height')}", "params": params,
                         "bindings": dict(STATS)})
            print(f"{v:52s} {kind:8s} bindings ok {STATS['ok']:4d}  kept stored {STATS['fail']:3d}")
        b.close()
    json.dump(meta, open(os.path.join(OUT, "templates", "index.json"), "w"), indent=1)
    return meta

if __name__ == "__main__":
    main()
