"""Static Ignition 8.1 import checks for every project folder in projects/.

    python3 tools/check_projects.py

Checks
  - project.json exists at the project root
  - every resource folder has resource.json listing files that exist
  - every .json file parses
  - Drawing (ia.shapes.svg) preserveAspectRatio is a bare 8.1 enum value (xMidYMid, not "xMidYMid meet")
  - every script (event scripts and script transforms) compiles as Python
  - every expression has balanced parentheses
Exit code 1 if anything fails. It cannot test the real gateway import or rendering.
"""
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ASPECT = {"none"} | {f"x{x}Y{y}" for x in ("Min", "Mid", "Max") for y in ("Min", "Mid", "Max")}
errors = []


def walk(o, f):
    if isinstance(o, dict):
        if o.get("type") == "ia.shapes.svg":
            par = o.get("props", {}).get("preserveAspectRatio")
            if par is not None and par not in ASPECT:
                errors.append(f"{f}: preserveAspectRatio '{par}' is not a bare 8.1 value")
        if o.get("type") == "script" and isinstance(o.get("code"), str):
            check_py("def transform(self, value, quality, timestamp):\n" + o["code"], f)
        if o.get("type") == "script" and isinstance(o.get("config"), dict) and "script" in o["config"]:
            check_py("def runAction(self, event):\n" + o["config"]["script"], f)
        if o.get("type") == "expr" and isinstance(o.get("config"), dict):
            e = o["config"].get("expression", "")
            if e.count("(") != e.count(")"):
                errors.append(f"{f}: unbalanced parentheses in expression: {e[:80]}")
        for v in o.values():
            walk(v, f)
    elif isinstance(o, list):
        for v in o:
            walk(v, f)


def check_py(src, f):
    try:
        compile(src + "\n", f, "exec")
    except SyntaxError as e:
        errors.append(f"{f}: script syntax error line {e.lineno}: {e.msg}")


def main():
    pdir = os.path.join(ROOT, "projects")
    for name in sorted(os.listdir(pdir)):
        proj = os.path.join(pdir, name)
        if not os.path.isdir(proj):
            continue
        if not os.path.isfile(os.path.join(proj, "project.json")):
            errors.append(f"{name}: missing project.json at the project root")
        n = 0
        for dp, dirs, files in os.walk(proj):
            for fn in files:
                if fn.endswith(".json"):
                    path = os.path.join(dp, fn)
                    rel = os.path.relpath(path, ROOT)
                    try:
                        data = json.load(open(path, encoding="utf-8"))
                    except Exception as e:
                        errors.append(f"{rel}: invalid JSON ({e})")
                        continue
                    walk(data, rel)
                    n += 1
            if "resource.json" in files:
                res = json.load(open(os.path.join(dp, "resource.json"), encoding="utf-8"))
                for f in res.get("files", []):
                    if not os.path.isfile(os.path.join(dp, f)):
                        errors.append(f"{os.path.relpath(dp, ROOT)}: resource.json lists missing file {f}")
        print(f"{name}: {n} JSON files checked")
    for dp, _, files in os.walk(os.path.join(ROOT, "tags")):
        for fn in files:
            if fn.endswith(".json"):
                try:
                    json.load(open(os.path.join(dp, fn), encoding="utf-8"))
                except Exception as e:
                    errors.append(f"{os.path.relpath(os.path.join(dp, fn), ROOT)}: invalid JSON ({e})")
    if errors:
        print("\nFAILED:")
        for e in errors:
            print("  " + e)
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
