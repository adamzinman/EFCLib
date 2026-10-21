# Archive

Kept for reference only. Nothing here is built, packaged or checked. Archived 2026-10-19 (v7.0) when the library was consolidated into the single `EFC_Library` project.

| Path | What it was | Why archived |
|---|---|---|
| `projects/PID_Compressor_Diaphragm/`, `generator/compressor_addon/`, `symbols/legacy/`, `mockups/compressor-diaphragm-addon.html` | Early single-symbol diaphragm compressor add-on | Superseded by `Templates/Rotating/Compressor_Diaphragm` |
| `generators-stale-copy/` | Older copies of the styles, PV, PID-symbol, loops, nav-connector and compressor generators (from the "first upload" commit) | Duplicates of `generator/`; the styles, PV and active-symbol files were older versions |
| `tools/build_all.py`, `check_projects.py`, `package.py` | The old build pipeline that drove `generators-stale-copy/` | Replaced by `build.py` |
| `tags/ProcessValues/PV_Demo_Tags.json` | Older PV demo tags | `tags/PV_Demo_Tags.json` is current |
| `docs/pid-symbol-index.md`, `pid-v3-notes.md`, `pv-display-notes.md` | v2 symbol index and pre-release design notes | Retired v2 views; notes already compiled into the current docs |

The seven separate v6.3 projects (EFC_Styles, PID_Symbols, EFC_PID_Library, EFC_ProcessValues, PID_Loops, EFC_IOFaceplates, EFC_StationFaceplates) are not copied here: they are regenerated from `generator/` and `imported/` into `EFC_Library`, and the exact v6.3 files are at git tag `v6.3`.
