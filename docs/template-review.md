# Template review (v7.0, 2026-10-19)

One image per view is in `docs/previews/templates/` (rendered from the real `view.json` files by `generator/render_views.py` against the demo tags). These came out of the first full render:

1. **BMXAMO0802 shows 8 channel rows; the card has 2.** The repeater's script transform hardcodes `n = 8`, so rows 2–7 show COMMS?. Fix in the Designer (set `n = 2`) and re-import with `tools/import_project_zip.py`.
2. **PID loop card headers collapse ("TIC101AUTO").** The loop cards' column flex containers don't set `alignItems`, so Perspective's default (`flex-start`) shrinks the header and rows to their content instead of the card width. The PV and Station templates set `alignItems: stretch` explicitly. Fix in `generator/pid_loops/generate_loops.py`; confirm on a gateway, since the loops have never been gateway-tested.

Renderer limits: it is a review aid, not Perspective. Alarm functions return "no alarm", trend charts are blank, and the I/O faceplates use a preview-only fake rack (`IO_Demo/Rack0`) because no I/O demo tags exist in `tags/`.
