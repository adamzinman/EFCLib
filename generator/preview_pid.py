import os
import preview as pv, build_pid as b4
from active import BY
figs=[]
for n,u,ov,sym in b4.DEMO:
    s=BY[sym]; tpl={"onoff":"AutoValve","control":"ControlValve"}.get(s.kind,"Motor")
    p={"symbol": sym if tpl!="Motor" else f"{s.cat}/{sym}", "alarm": 3 if ov.get("Fault") and u=="PID_Motor" else 0}
    orig=pv.LAYOUT[tpl]
    if tpl!="Motor": pv.LAYOUT[tpl]=b4.valve_layout(s,orig)
    nb = n in b4.NO_BUTTON
    figs.append(f"<figure><div style='zoom:2.3'>{pv.render(n,u,ov,tpl,p,not nb)}</div><figcaption><b>Templates/{s.cat}/{sym}</b><br>tagPath = [default]PID_Demo/{n}{'<br><i>useButton = false</i>' if nb else ''}</figcaption></figure>")
    pv.LAYOUT[tpl]=orig
open(os.path.join(b4.OUT,'preview.html'),'w').write(f"<html><head><meta charset=utf-8><style>{pv.CSS}</style></head><body><h2>Templates · demo tags · dark line = process line</h2><div class=row>{''.join(figs)}</div></body></html>")
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':900}); pg.goto('file://'+os.path.join(b4.OUT,'preview.html')); pg.screenshot(path=os.path.join(b4.OUT,'preview.png'),full_page=True); b.close()
