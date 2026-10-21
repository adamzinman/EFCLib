"""Navigation To/From connector shape options A-D (SVG only, no text inside; label overlaid in the parent view).
Writes symbols/NavConnectors/*.svg and mockups/nav-connectors.html."""
import os
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..",".."))
OUT=os.path.join(ROOT,"symbols","NavConnectors")
os.makedirs(OUT,exist_ok=True)
STROKE="#5A5A5A"; FILL="#F0F0F0"; DARK="#4A4A4A"; WHITE="#FFFFFF"
def svg(name,w,h,els):
    body="\n  ".join(els)
    s=f'<svg xmlns="http://www.w3.org/2000/svg" id="{name}" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n  {body}\n</svg>\n'
    open(f"{OUT}/{name}.svg","w").write(s); return s
def P(i,d,fill="none",stroke="none",sw=0,extra=""):
    st=f' stroke="{stroke}" stroke-width="{sw}"' if stroke!="none" else ' stroke="none"'
    return f'<path id="{i}" d="{d}" fill="{fill}"{st}{extra}/>'
def R(i,x,y,w,h,fill,stroke="none",sw=0,rx=0):
    st=f' stroke="{stroke}" stroke-width="{sw}"' if stroke!="none" else ' stroke="none"'
    r=f' rx="{rx}"' if rx else ''
    return f'<rect id="{i}" x="{x}" y="{y}" width="{w}" height="{h}"{r} fill="{fill}"{st}/>'
cap=' stroke-linecap="round" stroke-linejoin="round"'
S={}
# A: ISA off-page flag 160x32
S["A_Flag_To"]=(160,32,[P("body","M0.75,0.75 H143 L159.25,16 L143,31.25 H0.75 Z",FILL,STROKE,1.5)])
S["A_Flag_From"]=(160,32,[P("body","M0.75,0.75 H143 L159.25,16 L143,31.25 H0.75 L12,16 Z",FILL,STROKE,1.5)])
# B: Chevron tab 160x32
S["B_Chevron_To"]=(160,32,[R("body",0.75,0.75,158.5,30.5,FILL,STROKE,1.5,4),P("chevron","M142,9 L149,16 L142,23","none",DARK,2.5,cap)])
S["B_Chevron_From"]=(160,32,[R("body",0.75,0.75,158.5,30.5,FILL,STROKE,1.5,4),P("chevron","M18,9 L11,16 L18,23","none",DARK,2.5,cap)])
# C: Double chevron area jump 160x32
S["C_AreaJump_To"]=(160,32,[R("body",0.75,0.75,158.5,30.5,FILL,STROKE,1.5),R("cell",128,0.75,31.25,30.5,DARK),
  P("chevrons","M134,10 L140,16 L134,22 M143,10 L149,16 L143,22","none",WHITE,2.5,cap)])
S["C_AreaJump_From"]=(160,32,[R("body",0.75,0.75,158.5,30.5,FILL,STROKE,1.5),R("cell",0.75,0.75,31.25,30.5,DARK),
  P("chevrons","M26,10 L20,16 L26,22 M17,10 L11,16 L17,22","none",WHITE,2.5,cap)])
# D: Card with alarm slot + live value field 180x44
dia=lambda cx,cy,r: f"M{cx},{cy-r} L{cx+r},{cy} L{cx},{cy+r} L{cx-r},{cy} Z"
S["D_Card_To"]=(180,44,[P("body","M0.75,0.75 H158 L179.25,22 L158,43.25 H0.75 Z",FILL,STROKE,1.5),
  R("valueField",30,24,118,15,WHITE,STROKE,1),P("alarm",dia(15,22,9))])
S["D_Card_From"]=(180,44,[P("body","M0.75,0.75 H158 L179.25,22 L158,43.25 H0.75 L14,22 Z",FILL,STROKE,1.5),
  R("valueField",42,24,108,15,WHITE,STROKE,1),P("alarm",dia(29,22,8))])
svgs={k:svg(k,*v) for k,v in S.items()}
S=svgs

# ---------------------------------------------------------------- preview
import re
def inl(k,alarm=None):
    s=S[k]
    s=re.sub(r'<svg [^>]*id="([^"]+)"',lambda m:m.group(0).replace(f'id="{m.group(1)}"',''),s,count=1)
    if alarm: s=s.replace('<path id="alarm" d=','<path id="alarm" fill="%s" stroke="#222" stroke-width="1" d='%alarm).replace('fill="none" stroke="none"/>','/>',1) if False else s.replace('id="alarm"','id="alarm" style="fill:%s;stroke:#222;stroke-width:1"'%alarm)
    return s
opts=[
 ("A","Flag","A_Flag","ISA off-page connector",(160,32),"Classic P&amp;ID shape. Point = flow direction. The From version has a swallowtail.",(14,8),(26,8)),
 ("B","Chevron","B_Chevron","Chevron tab",(160,32),"Reads as a button. The chevron points toward the other screen.",(10,24),(26,10)),
 ("C","AreaJump","C_AreaJump","Area jump (double chevron)",(160,32),"Dark end cell with »/«. Use this for jumps to another area and A or B within an area.",(10,38),(40,10)),
 ("D","Card","D_Card","Card with alarm + live value",(180,44),"Pentagon with an ISA alarm slot (diamond) and a white live-value field.",(30,22),(42,22)),
]
rows=""
for L,_,base,title,(w,h),desc,(tl,tr),(fl,fr) in opts:
    two = L=="D"
    def lab(txt,val,l,r,top):
        if two:
            return f'<div class="lbl" style="left:{l}px;right:{r}px;top:3px;font-size:11px">{txt}</div><div class="val" style="left:{l+4}px;width:{(108 if top else 118)-8}px;top:24px">{val}</div>'
        return f'<div class="lbl" style="left:{l}px;right:{r}px;top:0;height:{h}px;line-height:{h}px">{txt}</div>'
    frm=f'<div class="conn" style="width:{w}px;height:{h}px">{inl(base+"_From","#F5A623" if two else None)}{lab("FROM: TANK FARM","142.6 GPM",fl,fr,1)}</div>'
    to=f'<div class="conn" style="width:{w}px;height:{h}px">{inl(base+"_To","#D0021B" if two else None)}{lab("TO: AREA 2 REACTOR","38.1 PSIG",tl,tr,0)}</div>'
    rows+=f'''<section><h2>Option {L} — {title}</h2><p>{desc}</p>
<div class="canvas">{frm}<div class="pipe"></div><div class="equip">P-101</div><div class="pipe"></div>{to}</div>
<div class="files">svg/{base}_From.svg · svg/{base}_To.svg · {w}×{h} px @1080p</div></section>'''
html=f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nav Connector Options</title>
<style>
body{{margin:0;padding:24px 16px;background:#C8C8C8;font-family:Arial,Helvetica,sans-serif;color:#222}}
h1{{font-size:20px;margin:0 0 4px}} .sub{{margin:0 0 20px;font-size:13px;color:#444}}
section{{background:#D9D9D9;border:1px solid #AAA;border-radius:6px;padding:14px 16px;margin-bottom:16px;max-width:900px}}
h2{{font-size:15px;margin:0 0 4px}} p{{font-size:13px;margin:0 0 12px;color:#333}}
.canvas{{display:flex;align-items:center;overflow-x:auto;padding:10px 0}}
.conn{{position:relative;flex:none;cursor:pointer}} .conn svg{{display:block}}
.conn:hover svg #body{{fill:#E0E0E0}}
.lbl{{position:absolute;font-size:11px;font-weight:bold;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.val{{position:absolute;height:15px;line-height:15px;font-size:11px;text-align:right;font-family:Consolas,monospace}}
.pipe{{flex:1;min-width:40px;height:3px;background:#5A5A5A}}
.equip{{flex:none;width:70px;height:46px;border:1.5px solid #5A5A5A;background:#F0F0F0;border-radius:23px;display:flex;align-items:center;justify-content:center;font-size:11px}}
.files{{font-size:11px;color:#555;margin-top:6px;font-family:Consolas,monospace}}
</style></head><body><h1>Nav connector options: To / From</h1>
<p class="sub">Each row shows a FROM connector at the left edge and a TO connector at the right edge, as on a process screen. Text and values are HTML overlays here, the same way they'll be labels in the parent Perspective view. Hover to see a fill change.</p>
{rows}</body></html>'''
open(os.path.join(ROOT,"mockups","nav-connectors.html"),"w").write(html)
