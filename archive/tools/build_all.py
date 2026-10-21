"""Regenerate every generated folder in the repo from the generators.

    python3 tools/build_all.py            # rebuild everything
    python3 tools/build_all.py loops      # only the generators whose name contains "loops"

What it does
  generators/pid_loops         -> projects/PID_Loops, tags/PID_Loops
  generators/compressor_addon  -> projects/PID_Compressor_Diaphragm, symbols/legacy, mockups/
  generators/nav_connectors    -> symbols/NavConnectors, mockups/nav-connectors.html
  generators/efc_styles        -> projects/EFC_Styles (unzipped), docs/style-class-index.md, mockups/style-preview.html
  generators/process_values    -> projects/EFC_ProcessValues (unzipped), tags/ProcessValues, docs/pv-style-index.md

Then run tools/check_projects.py and tools/package.py.
"""
import os, shutil, subprocess, sys, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
GEN = os.path.join(ROOT, "generators")


def run(script):
    print(f"--> {os.path.relpath(script, ROOT)}")
    subprocess.run([sys.executable, os.path.basename(script)], cwd=os.path.dirname(script), check=True)


def unzip_project(zpath, name):
    dest = os.path.join(ROOT, "projects", name)
    shutil.rmtree(dest, ignore_errors=True)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(dest)
    print(f"    extracted {os.path.basename(zpath)} -> projects/{name}")


def copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(src, dst)


def loops():
    run(os.path.join(GEN, "pid_loops", "generate_loops.py"))


def compressor():
    run(os.path.join(GEN, "compressor_addon", "generate_compressor.py"))


def nav():
    run(os.path.join(GEN, "nav_connectors", "generate_nav_connectors.py"))


def styles():
    d = os.path.join(GEN, "efc_styles")
    run(os.path.join(d, "build_styles.py"))
    unzip_project(os.path.join(d, "dist", "EFC_Styles.zip"), "EFC_Styles")
    copy(os.path.join(d, "dist", "style_index.md"), os.path.join(ROOT, "docs", "style-class-index.md"))
    copy(os.path.join(d, "dist", "style_preview.html"), os.path.join(ROOT, "mockups", "style-preview.html"))
    shutil.rmtree(os.path.join(d, "dist"))


def process_values():
    d = os.path.join(GEN, "process_values")
    run(os.path.join(d, "build_pv.py"))
    unzip_project(os.path.join(d, "dist", "EFC_ProcessValues.zip"), "EFC_ProcessValues")
    copy(os.path.join(d, "dist", "PV_Demo_Tags.json"), os.path.join(ROOT, "tags", "ProcessValues", "PV_Demo_Tags.json"))
    copy(os.path.join(d, "dist", "pv_style_index.md"), os.path.join(ROOT, "docs", "pv-style-index.md"))
    shutil.rmtree(os.path.join(d, "dist"))


STEPS = {"loops": loops, "compressor": compressor, "nav": nav, "styles": styles, "process_values": process_values}

if __name__ == "__main__":
    want = sys.argv[1:]
    for name, fn in STEPS.items():
        if not want or any(w in name for w in want):
            fn()
    print("done")
