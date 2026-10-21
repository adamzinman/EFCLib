"""Diaphragm compressor add-on symbol (2026-10-05, full-circle version with diaphragm arc).
SUPERSEDED by Templates/Rotating/Compressor_Diaphragm in PID_Symbols v5.1 (arc removed, note 29). Kept for reference.
Writes projects/PID_Compressor_Diaphragm, symbols/legacy and mockups/."""
import json, os, math, shutil
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..",".."))
PROJ=os.path.join(ROOT,"projects","PID_Compressor_Diaphragm")
shutil.rmtree(PROJ,ignore_errors=True)
PX=64; k=100/PX                      # native 64 px at 1080p, 100x100 box
OUTLINE=round(1.5*k,2); DETAIL=round(1.0*k,2); ALARMW=round(3.0*k,2)
STROKE="#4D4D4D"
FILL={0:"#B4B4B4",1:"#FFFFFF",2:"#DCDCDC",3:"#E0001B"}
ALARM={1:"#00A0E0",2:"#FFD700",3:"#FF8C00",4:"#E0001B"}
cx,cy,r=50,50,38
def onc(dy,side): return round(cx+side*math.sqrt(r*r-dy*dy),2)
DL,DR=16.5,7.5
xl,xr=onc(DL,-1),onc(DR,1)
tl,bl=(xl,cy-DL),(xl,cy+DL); tr,br=(xr,cy-DR),(xr,cy+DR)
# body = circle + base merged into one closed path (one fill binding)
ang=math.degrees(math.asin(14/r)); bx=round(math.sqrt(r*r-26*26),2)  # base meets circle at y=76
body=(f"M{cx-bx},{cy+26} A{r},{r} 0 1 1 {cx+bx},{cy+26} "
      f"L{cx+26},{cy+38} H{cx-26} Z")
detail=(f"M{tl[0]},{tl[1]} L{tr[0]},{tr[1]} M{bl[0]},{bl[1]} L{br[0]},{br[1]} "
        )                                                    # compressor trapezoid
xd=38; hd=round(DL-(DL-DR)*(xd-xl)/(xr-xl)-0.6,2)
diaphragm=f"M{xd},{cy-hd} Q{xd+26},{cy} {xd},{cy+hd}"                         # diaphragm, outline weight
nozzles=f"M6,50 H{cx-r} M{cx+r},50 H94"                    # suction left, discharge right
els=[("path","nozzles",{"d":nozzles},"none",STROKE,OUTLINE),
     ("circle","body",{"cx":cx,"cy":cy,"r":r},FILL[0],STROKE,OUTLINE),
     ("path","detail",{"d":detail},"none",STROKE,DETAIL),
     ("path","diaphragm",{"d":diaphragm},"none",STROKE,round(2.0*k,2))]
# --- static SVG
def attrs(a): return " ".join(f'{k}="{v}"' for k,v in a.items())
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" id="Compressor_Diaphragm" width="{PX}" height="{PX}" viewBox="0 0 100 100">']
for t,n,a,f,s,w in els:
    svg.append(f'  <{t} id="{n}" {attrs(a)} fill="{f}" stroke="{s}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>')
svg.append("</svg>\n")
os.makedirs(f"{ROOT}/symbols/legacy",exist_ok=True)
open(f"{ROOT}/symbols/legacy/Compressor_Diaphragm_addon.svg","w").write("\n".join(svg))
# --- Perspective view (8.1)
E=[]
for t,n,a,f,s,w in els:
    e={"type":t,"name":n,**a,"fill":{"paint":f},"stroke":{"paint":s,"width":w}}
    E.append(e)
fillExpr=("case({view.params.state},0,'%s',1,'%s',2,'%s',3,'%s','%s')"%(FILL[0],FILL[1],FILL[2],FILL[3],FILL[0]))
strokeExpr=("case({view.params.alarm},1,'%s',2,'%s',3,'%s',4,'%s','%s')"%(ALARM[1],ALARM[2],ALARM[3],ALARM[4],STROKE))
widthExpr=f"if({{view.params.alarm}}>0,{ALARMW},{OUTLINE})"
pb=lambda p:{"binding":{"type":"property","config":{"path":p}}}
view={
 "custom":{"fill":FILL[0],"outline":STROKE,"outlineWidth":OUTLINE},
 "params":{"state":0,"alarm":0},
 "propConfig":{
   "custom.fill":{"binding":{"type":"expr","config":{"expression":fillExpr}}},
   "custom.outline":{"binding":{"type":"expr","config":{"expression":strokeExpr}}},
   "custom.outlineWidth":{"binding":{"type":"expr","config":{"expression":widthExpr}}},
   "params.state":{"paramDirection":"input","persistent":True},
   "params.alarm":{"paramDirection":"input","persistent":True}},
 "props":{"defaultSize":{"width":PX,"height":PX}},
 "root":{"type":"ia.container.flex","meta":{"name":"root"},
   "props":{"direction":"column"},
   "children":[{"type":"ia.shapes.svg","meta":{"name":"Compressor_Diaphragm"},
     "position":{"basis":"100%","grow":1,"shrink":1},
     "props":{"viewBox":"0 0 100 100","preserveAspectRatio":"xMidYMid","elements":E},
     "propConfig":{
       "props.elements[1].fill.paint":pb("view.custom.fill"),
       "props.elements[1].stroke.paint":pb("view.custom.outline"),
       "props.elements[1].stroke.width":pb("view.custom.outlineWidth")}}]}}
vdir=f"{PROJ}/com.inductiveautomation.perspective/views/PID/Rotating/Compressor_Diaphragm"
os.makedirs(vdir)
json.dump(view,open(f"{vdir}/view.json","w"),indent=2)
json.dump({"scope": "G", "version": 1, "restricted": False, "overridable": True, "files": ["view.json"], "attributes": {"lastModification": {"actor": "admin", "timestamp": "2026-10-05T12:00:00Z"}}},open(f"{vdir}/resource.json","w"),indent=2)
json.dump({"title":"PID_Compressor_Diaphragm","description":"Diaphragm gas compressor symbol","parent":"","enabled":True,"inheritable":True},open(f"{PROJ}/project.json","w"),indent=2)
# --- preview of all states
def variant(fill,stroke,w):
    s="\n".join(svg).replace(f'fill="{FILL[0]}" stroke="{STROKE}" stroke-width="{OUTLINE}"',f'fill="{fill}" stroke="{stroke}" stroke-width="{w}"')
    return s.replace('width="64" height="64"','width="128" height="128"')
cells=[(f"state {i}",variant(FILL[i],STROKE,OUTLINE),n) for i,n in [(0,"stopped"),(1,"running"),(2,"transition"),(3,"fault")]]
cells+=[(f"alarm {i}",variant(FILL[1],ALARM[i],ALARMW),n) for i,n in [(1,"low"),(2,"medium"),(3,"high"),(4,"critical")]]
grid="".join(f'<div class="c">{s}<b>{t}</b><span>{n}</span></div>' for t,s,n in cells)
html=f'''<!doctype html><html><head><meta charset="utf-8"><title>Diaphragm Compressor</title><style>
body{{margin:0;padding:24px 16px;background:#D9D9D9;font-family:Arial,sans-serif;color:#222}}
h1{{font-size:18px;margin:0 0 4px}}p{{font-size:13px;margin:0 0 16px}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;max-width:760px}}
.c{{background:#E6E6E6;border:1px solid #BBB;border-radius:6px;padding:10px;text-align:center}}
.c svg{{display:block;margin:0 auto 6px}}b{{display:block;font-size:13px}}span{{font-size:12px;color:#555}}
.n{{margin-top:20px;display:flex;align-items:center;gap:24px}}</style></head><body>
<h1>Compressor_Diaphragm (64 px native, shown at 2×)</h1><p>Suction on the left, discharge on the right, both on the y=50 centerline. Every combination of the <code>state</code> and <code>alarm</code> params is shown.</p>
<div class="g">{grid}</div>
<div class="n">{"".join(svg)}<span>Actual 1080p size (64 px)</span></div></body></html>'''
open(f"{ROOT}/mockups/compressor-diaphragm-addon.html","w").write(html)
