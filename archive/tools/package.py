"""Zip every folder in projects/ into dist/<Name>_PROJECT.zip, ready for Ignition import.

    python3 tools/package.py             # all projects
    python3 tools/package.py PID_Loops   # just one

project.json is placed at the zip root (the gateway import fails if the project is nested in a folder).
Tag JSON files are copied to dist/tags/. dist/ is ignored by git.
"""
import os, shutil, sys, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DIST = os.path.join(ROOT, "dist")


def package(name):
    src = os.path.join(ROOT, "projects", name)
    if not os.path.isfile(os.path.join(src, "project.json")):
        raise SystemExit(f"{name}: no project.json at {src}")
    out = os.path.join(DIST, f"{name}_PROJECT.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(src, "project.json"), "project.json")
        for dp, _, files in os.walk(src):
            for f in sorted(files):
                full = os.path.join(dp, f)
                rel = os.path.relpath(full, src).replace(os.sep, "/")
                if rel != "project.json":
                    z.write(full, rel)
    print(f"dist/{name}_PROJECT.zip")


if __name__ == "__main__":
    os.makedirs(DIST, exist_ok=True)
    names = sys.argv[1:] or sorted(d for d in os.listdir(os.path.join(ROOT, "projects"))
                                   if os.path.isdir(os.path.join(ROOT, "projects", d)))
    for n in names:
        package(n)
    tdst = os.path.join(DIST, "tags")
    shutil.rmtree(tdst, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, "tags"), tdst)
    print("dist/tags/")
