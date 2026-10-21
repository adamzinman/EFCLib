#!/usr/bin/env python3
"""
EFC Ignition library build. Everything ships as ONE Perspective project, EFC_Library (no parent):
EFC_Styles classes + stylesheet, PID_Symbols, EFC_ProcessValues, PID_Loops (all generated here) and the
imported projects in imported/ (EFC_IOFaceplates, EFC_StationFaceplates), merged under a single views/Templates/ tree.

    python3 build.py              regenerate everything tracked in git (projects/, tags/, symbols/, docs/style-class-index.md)
    python3 build.py --preview    also render docs/previews/templates.png and one PNG per view in
                                  docs/previews/templates/ (needs Playwright + Chromium)
    python3 build.py --dist       also write importable zips to dist/ (gitignored)
    python3 build.py --check      check the committed projects/ only (no regeneration); used by CI

The generator (generator/) and imported/ are the sources. projects/EFC_Library is generated: the merged project
unzipped in the gateway's own folder layout (data/projects/<Name>/...), so every change shows as a readable JSON
diff and the folder can be copied straight onto a gateway. The per-part projects are built in build/components/
(gitignored) and only exist as intermediates.
"""
import argparse, json, os, re, shutil, subprocess, sys, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(ROOT, "generator")
BUILD = os.path.join(ROOT, "build")
DIST = os.path.join(ROOT, "dist")
PROJECTS = os.path.join(ROOT, "projects")
IMPORTED = os.path.join(ROOT, "imported")
COMPONENTS = os.path.join(BUILD, "components")
VERSION = json.load(open(os.path.join(ROOT, "VERSION.json")))
LIBRARY = "EFC_Library"
GENERATED_PARTS = ("EFC_Styles", "PID_Symbols", "EFC_ProcessValues", "PID_Loops")
IMPORTED_PARTS = ("EFC_IOFaceplates", "EFC_StationFaceplates")

# Views that don't already live under Templates/ are moved there in the merged project. Every string that
# names one of these view paths (embedded views, flex repeaters, openPopup calls) is rewritten to match.
RELOCATE = {
    "PID_Loops": [("PID/Templates/", "Templates/Loops/"), ("PID/Popups/", "Templates/Loops/Popups/"),
                  ("PID/_Demo_Loops", "Templates/Loops/_Demo")],
    "EFC_IOFaceplates": [("IO/", "Templates/IO/")],
}


def run(*args, **kw):
    subprocess.run([sys.executable, *args], cwd=GEN, check=True, **kw)


def unzip_to(zp, dest):
    """Replace dest with the zip's contents (files only; directory entries are implied)."""
    if os.path.exists(dest):
        shutil.rmtree(dest)
    with zipfile.ZipFile(zp) as z:
        for n in z.namelist():
            if n.endswith("/"):
                continue
            p = os.path.join(dest, n)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            data = z.read(n)
            if n.endswith(".json"):          # normalise: LF endings + trailing newline for clean diffs
                data = data.replace(b"\r\n", b"\n").rstrip(b"\n") + b"\n"
            open(p, "wb").write(data)


def zip_dir(src, zp):
    """Zip a project folder the way a Designer export looks (project.json first, then folder entries)."""
    sys.path.insert(0, GEN)
    from make_project_zip import redo
    raw = zp + ".raw"
    with zipfile.ZipFile(raw, "w", zipfile.ZIP_DEFLATED) as z:
        for d, _, fs in sorted(os.walk(src)):
            for f in sorted(fs):
                p = os.path.join(d, f)
                z.write(p, os.path.relpath(p, src).replace(os.sep, "/"))
    redo(raw, zp)
    os.remove(raw)


def replace_tree(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def project_json(title, description, parent=""):
    return {"title": title, "description": description, "parent": parent, "enabled": True, "inheritable": True}


def generate(preview):
    os.environ["EFC_BUILD_TIMESTAMP"] = VERSION["date"] + "T00:00:00Z"
    v = VERSION["version"]
    run("build_styles.py", stdout=subprocess.DEVNULL)
    run("build_pid.py")
    if preview:
        run("preview_pid.py")

    # build the generated parts (EFC_Styles, PID_Symbols) in projects/; merge_library() moves them to build/components/
    unzip_to(os.path.join(BUILD, "styles", "EFC_Styles.zip"), os.path.join(PROJECTS, "EFC_Styles"))
    unzip_to(os.path.join(BUILD, "pid", "PID_Symbols_PROJECT.zip"), os.path.join(PROJECTS, "PID_Symbols"))
    for name, desc, parent in (("EFC_Styles", f"EFC ISA-101 style class library v{v} (generated)", ""),
                               ("PID_Symbols", f"EFC controlled-device templates v{v} (generated). Parent: EFC_Styles", "EFC_Styles")):
        with open(os.path.join(PROJECTS, name, "project.json"), "w") as f:
            json.dump(project_json(name, desc, parent), f, indent=2); f.write("\n")
    # tags/: overwrite the generated PID files only; imported tag files (e.g. Station demo) are kept
    os.makedirs(os.path.join(ROOT, "tags"), exist_ok=True)
    for f in os.listdir(os.path.join(BUILD, "pid", "tags")):
        shutil.copy(os.path.join(BUILD, "pid", "tags", f), os.path.join(ROOT, "tags", f))
    replace_tree(os.path.join(BUILD, "pid", "symbols"), os.path.join(ROOT, "symbols"))
    shutil.copy(os.path.join(BUILD, "styles", "style_index.md"), os.path.join(ROOT, "docs", "style-class-index.md"))
    run("build_pv.py")                    # EFC_ProcessValues -> projects/, tags/PV_Demo_Tags.json, docs/pv-style-index.md
    run("pid_loops/generate_loops.py")           # PID_Loops -> projects/PID_Loops, tags/PID_Loops/
    run("nav_connectors/generate_nav_connectors.py")   # symbols/NavConnectors, mockups/nav-connectors.html
    merge_library()
    os.makedirs(os.path.join(ROOT, "mockups"), exist_ok=True)
    shutil.copy(os.path.join(BUILD, "styles", "style_preview.html"), os.path.join(ROOT, "mockups", "style-preview.html"))
    if preview:
        run("render_views.py")            # docs/previews/templates/<Category>/<Name>.png, one per view
        os.makedirs(os.path.join(ROOT, "docs", "previews"), exist_ok=True)
        shutil.copy(os.path.join(BUILD, "pid", "preview.png"), os.path.join(ROOT, "docs", "previews", "templates.png"))


def relocate(part, rel):
    """New path (relative to the project root) for a file of `part` in the merged project."""
    pre = "com.inductiveautomation.perspective/views/"
    if rel.startswith(pre):
        v = rel[len(pre):]
        for old, new in RELOCATE.get(part, []):
            if v.startswith(old):
                return pre + new + v[len(old):]
    return rel


def rewrite_refs(part, text):
    """Rewrite view-path strings (plain JSON "IO/..." and escaped script \\"IO/..." alike)."""
    for old, new in RELOCATE.get(part, []):
        text = re.sub(r'(?<=["\\])' + re.escape(old), new, text)
    return text


def merge_library():
    """Move the generated parts to build/components/ and merge them with imported/ into projects/EFC_Library."""
    os.makedirs(COMPONENTS, exist_ok=True)
    for name in GENERATED_PARTS:
        src = os.path.join(PROJECTS, name)
        replace_tree(src, os.path.join(COMPONENTS, name))
        shutil.rmtree(src)
    lib = os.path.join(PROJECTS, LIBRARY)
    if os.path.exists(lib):
        shutil.rmtree(lib)
    owner = {}
    parts = [(n, os.path.join(COMPONENTS, n)) for n in GENERATED_PARTS] + [(n, os.path.join(IMPORTED, n)) for n in IMPORTED_PARTS]
    for name, src in parts:
        for d, _, fs in os.walk(src):
            for f in fs:
                rel = os.path.relpath(os.path.join(d, f), src).replace(os.sep, "/")
                if rel == "project.json":
                    continue
                new = relocate(name, rel)
                if new in owner:
                    sys.exit(f"merge conflict: {new} comes from both {owner[new]} and {name}")
                owner[new] = name
                data = open(os.path.join(d, f), "rb").read()
                if f.endswith(".json") and name in RELOCATE:
                    data = rewrite_refs(name, data.decode("utf-8")).encode("utf-8")
                dest = os.path.join(lib, new)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                open(dest, "wb").write(data)
    v = VERSION["version"]
    with open(os.path.join(lib, "project.json"), "w") as f:
        json.dump(project_json(LIBRARY, f"EFC Ignition library v{v} (generated): ISA-101 styles, P&ID device templates, process values, "
                                        "PID loops, x80 I/O card and station faceplates in one project. Import standalone, or make it "
                                        "the parent of an HMI project."), f, indent=2); f.write("\n")
    check_view_refs(lib)


def check_view_refs(lib):
    """Every embedded view, repeater and literal openPopup path must name a view that exists in the library."""
    vroot = os.path.join(lib, "com.inductiveautomation.perspective", "views")
    views = {os.path.relpath(d, vroot).replace(os.sep, "/") for d, _, fs in os.walk(vroot) if "view.json" in fs}
    bad = []
    for v in views:
        txt = open(os.path.join(vroot, v, "view.json")).read()
        refs = re.findall(r'"path": "((?:Templates|Styles)/[^"]+)"', txt)
        refs += [m for m in re.findall(r'openPopup\([^,]+, \\"([^"\\]+)\\"', txt)]
        prefixes = re.findall(r'openPopup\([^,]+, \\"([^"\\]+/)\\" \+', txt)
        for r in refs:
            if not r.endswith("/") and r not in views:
                bad.append(f"{v} -> {r}")
        for p in prefixes:
            if not any(x.startswith(p) for x in views):
                bad.append(f"{v} -> {p}*")
    if bad:
        sys.exit("broken view references:\n  " + "\n  ".join(sorted(set(bad))))
    print(f"{LIBRARY}: {len(views)} views, all view references resolve")


def make_dist():
    os.makedirs(DIST, exist_ok=True)
    v = VERSION["version"]
    out = []
    for name in sorted(os.listdir(PROJECTS)):          # every project folder, generated or imported
        if not os.path.isfile(os.path.join(PROJECTS, name, "project.json")):
            continue
        zp = os.path.join(DIST, f"{name}_PROJECT.zip")
        zip_dir(os.path.join(PROJECTS, name), zp)
        out.append(zp)
    bundle = os.path.join(DIST, f"EFC_Ignition_Library_v{v}.zip")     # everything in one download for people without git
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as z:
        for sub in ("tags", "symbols"):
            for d, _, fs in sorted(os.walk(os.path.join(ROOT, sub))):
                for f in sorted(fs):
                    p = os.path.join(d, f)
                    z.write(p, f"EFC_Ignition_Library_v{v}/" + os.path.relpath(p, ROOT))
        for zp in out:
            z.write(zp, f"EFC_Ignition_Library_v{v}/" + os.path.basename(zp))
        for f in ("README.md", "CHANGELOG.md"):
            z.write(os.path.join(ROOT, f), f"EFC_Ignition_Library_v{v}/{f}")
    return out


def check(zips):
    run("check_81.py", *zips)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preview", action="store_true", help="render docs/previews/templates.png (Playwright)")
    ap.add_argument("--dist", action="store_true", help="write importable project zips to dist/")
    ap.add_argument("--check", action="store_true", help="only run the 8.1 import check on the committed projects/")
    a = ap.parse_args()
    if not a.check:
        generate(a.preview)
    zips = make_dist() if (a.dist or a.check) else None
    if zips is None:                      # check from temporary zips so the check always runs
        import tempfile
        global DIST
        DIST = tempfile.mkdtemp()
        zips = make_dist()
    check(zips)
    print(f"v{VERSION['version']} OK" + (f"  ->  {DIST}" if a.dist else ""))


if __name__ == "__main__":
    main()
