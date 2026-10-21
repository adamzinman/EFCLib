"""Shared helpers for build_pv.py: repo paths, version stamp and deterministic writers (LF, trailing newline, fixed timestamps)."""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_V = json.load(open(os.path.join(REPO, "VERSION.json")))
VERSION, DATE = _V["version"], _V["date"]
PERSPECTIVE = "com.inductiveautomation.perspective"

def dump(obj):
    return json.dumps(obj, indent=2) + "\n"

def write(path, text, binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if binary:
        open(path, "wb").write(text)
    else:
        with open(path, "w", newline="\n", encoding="utf-8") as fh:
            fh.write(text)

def resource_json(files, actor):
    """8.1 resource.json. The timestamp comes from VERSION.json so rebuilds are byte-identical."""
    return dump({"scope": "G", "version": 1, "restricted": False, "overridable": True, "files": files,
                 "attributes": {"lastModification": {"actor": "efc-ignition-library", "timestamp": DATE + "T00:00:00Z"}}})

def project_json(title, description, parent=""):
    return dump({"title": title, "description": f"{description} (v{VERSION}, generated)", "parent": parent,
                 "enabled": True, "inheritable": True})

def project_dir(name):
    return os.path.join(REPO, "projects", name)
