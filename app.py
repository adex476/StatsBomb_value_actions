from flask import Flask, Response
import json, os

app = Flask(__name__)

def _base_dir():
    # Works whether run as a script or from a notebook
    return os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()

@app.route("/sequence.json")
def sequence_json():
    path = os.path.join(_base_dir(), "sequence.json")
    if not os.path.exists(path):
        return Response(json.dumps({"error": f"sequence.json not found at {path}"}), status=404, mimetype="application/json")
    with open(path, "r", encoding="utf-8") as f:
        return Response(f.read(), mimetype="application/json")

@app.route("/ping")
def ping():
    return "pong"
@app.route("/")
def index():
    return Response(r"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>xG Pitch (possession story)</title>
<style>
:root{--bg:#0b0d10;--card:#11151a;--grid:#4a5363;--home:#60a5fa;--away:#f472b6;--muted:#94a3b8}
body{margin:0;font-family:Inter,system-ui,Segoe UI,Roboto,Arial;background:var(--bg);color:#e5e7eb}
.wrap{max-width:1200px;margin:18px auto;padding:0 16px}
.card{background:var(--card);border-radius:14px;box-shadow:0 8px 24px rgba(0,0,0,.25);padding:14px}
.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.controls>*{font-size:12px;color:#cbd5e1}
button{background:#1f2937;color:#e5e7eb;border:1px solid #2a2f37;border-radius:10px;padding:6px 10px;cursor:pointer}
button:hover{background:#263244}
.grid{display:grid;grid-template-columns: minmax(420px,1fr) 320px;gap:12px}
svg{width:100%;height:auto}
.kpi{margin:6px 0 8px 0;color:#cbd5e1;font-size:13px}
.msg{color:var(--muted);font-size:12px}
.timeline{list-style:none;margin:0;padding:0;max-height:520px;overflow:auto}
.timeline li{padding:6px 8px;border-bottom:1px solid #222a33;display:flex;gap:8px;align-items:center}
.badge{background:#0e1723;border:1px solid #2a2f37;border-radius:999px;padding:2px 7px;font-size:11px}
.type{color:#cbd5e1;font-size:12px}
.ply{color:#9fb3c8}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block}
</style>
</head>
<body>
<div class="wrap">
  <div class="card" style="margin-bottom:12px">
    <div class="controls">
      <button id="reload">Reload JSON</button>
      <label><input type="checkbox" id="onlyOnBall" checked> Only on-ball</label>
      <label><input type="checkbox" id="numberSteps" checked> Number steps</label>
      <label><input type="checkbox" id="showPath" checked> Show path</label>
      <label><input type="checkbox" id="flip"> Flip attack → right</label>
      <label><input type="checkbox" id="finalThird"> Zoom final third</label>
      <label>Min hop (m): <input id="mind" type="number" value="3" min="0" max="15" step="1" style="width:48px;background:#0e1723;color:#e5e7eb;border:1px solid #2a2f37;border-radius:6px;padding:2px 6px"></label>
      <span style="margin-left:auto">home=<span class="dot" style="background:var(--home)"></span> away=<span class="dot" style="background:var(--away)"></span></span>
    </div>
    <div id="kpi" class="kpi">Cumulative xG: –</div>
    <div id="msg" class="msg"></div>
  </div>

  <div class="grid">
    <div class="card" style="position:relative">
      <svg id="pitch" viewBox="-3 -3 126 86" aria-label="pitch"></svg>
    </div>
    <div class="card">
      <div style="font-weight:600;margin-bottom:8px">Possession timeline</div>
      <ul id="timeline" class="timeline"></ul>
    </div>
  </div>
</div>

<script>
const $=s=>document.querySelector(s);
const pitch=$('#pitch'), kpi=$('#kpi'), msg=$('#msg'), tl=$('#timeline');
const chkOnBall=$('#onlyOnBall'), chkNums=$('#numberSteps'), chkPath=$('#showPath'), chkFlip=$('#flip'), chkThird=$('#finalThird'), minDistInput=$('#mind');

function n(tag){return document.createElementNS('http://www.w3.org/2000/svg',tag)}
function line(p,x1,y1,x2,y2,stroke='#9aa5b5',w=1.6,op=.7){const e=n('line');e.setAttribute('x1',x1);e.setAttribute('y',y1);e.setAttribute('x2',x2);e.setAttribute('y2',y2);e.setAttribute('stroke',stroke);e.setAttribute('stroke-width',w);e.setAttribute('opacity',op);e.setAttribute('stroke-linecap','round');p.appendChild(e)}
function rect(p,x,y,w,h,stroke='#4a5363'){const e=n('rect');e.setAttribute('x',x);e.setAttribute('y',y);e.setAttribute('width',w);e.setAttribute('height',h);e.setAttribute('fill','none');e.setAttribute('stroke',stroke);e.setAttribute('stroke-width','1.1');p.appendChild(e)}
function circle(p,cx,cy,r,fill,op=.95){const e=n('circle');e.setAttribute('cx',cx);e.setAttribute('cy',cy);e.setAttribute('r',r);e.setAttribute('fill',fill);e.setAttribute('opacity',op);p.appendChild(e)}
function ring(p,cx,cy,r,stroke='#f8cc4a',w=2){const e=n('circle');e.setAttribute('cx',cx);e.setAttribute('cy',cy);e.setAttribute('r',r);e.setAttribute('fill','none');e.setAttribute('stroke',stroke);e.setAttribute('stroke-width',w);p.appendChild(e)}
function text(p,x,y,t,fill='#0b0d10',size=8.5){const e=n('text');e.setAttribute('x',x);e.setAttribute('y',y);e.setAttribute('fill',fill);e.setAttribute('font-size',size);e.setAttribute('text-anchor','middle');e.setAttribute('dominant-baseline','central');e.textContent=t;p.appendChild(e)}
function arrow(p,x1,y1,x2,y2,stroke,w=1.6,op=.9){const e=n('line');e.setAttribute('x1',x1);e.setAttribute('y1',y1);e.setAttribute('x2',x2);e.setAttribute('y2',y2);e.setAttribute('stroke',stroke);e.setAttribute('stroke-width',w);e.setAttribute('opacity',op);e.setAttribute('stroke-linecap','round');p.appendChild(e);const a=Math.atan2(y2-y1,x2-x1),L=2.6;const ax=x2-L*Math.cos(a-Math.PI/8),ay=y2-L*Math.sin(a-Math.PI/8),bx=x2-L*Math.cos(a+Math.PI/8),by=y2-L*Math.sin(a+Math.PI/8);const h=n('polyline');h.setAttribute('points',`${ax},${ay} ${x2},${y2} ${bx},${by}`);h.setAttribute('fill','none');h.setAttribute('stroke',stroke);h.setAttribute('stroke-width',w);h.setAttribute('opacity',op);h.setAttribute('stroke-linecap','round');h.setAttribute('stroke-linejoin','round');p.appendChild(h)}

function drawPitch(){
  pitch.innerHTML='';
  const g=n('g'); rect(g,0,0,120,80); // outlines
  // centre line + circle
  const mid=n('line'); mid.setAttribute('x1',60); mid.setAttribute('y1',0); mid.setAttribute('x2',60); mid.setAttribute('y2',80); mid.setAttribute('stroke', '#4a5363'); mid.setAttribute('stroke-width','1.1'); g.appendChild(mid);
  const cc=n('circle'); cc.setAttribute('cx',60); cc.setAttribute('cy',40); cc.setAttribute('r',9.15); cc.setAttribute('fill','none'); cc.setAttribute('stroke','#4a5363'); cc.setAttribute('stroke-width','1.1'); g.appendChild(cc);
  // boxes
  rect(g,0,18,18,44); rect(g,0,29.92,6,20.16); rect(g,102,18,18,44); rect(g,114,29.92,6,20.16);
  // attack arrow (right)
  const a=n('polyline'); a.setAttribute('points','104,6 116,6 112,3 116,6 112,9'); a.setAttribute('fill','none'); a.setAttribute('stroke','#6e7a89'); a.setAttribute('stroke-width','1.2'); g.appendChild(a);
  pitch.appendChild(g);
}

function scaleTo120x80(e){ const needs=Math.max(e.x??0,e.y??0,e.end_x??0,e.end_y??0)<=100; const sx=needs?1.2:1, sy=needs?0.8:1; return { x:(+e.x||0)*sx, y:(+e.y||0)*sy, ex:(+e.end_x||+e.x||0)*sx, ey:(+e.end_y||+e.y||0)*sy }; }
function flipX(v){return 120-v;}
function isOnBall(e){ const t=(e.event||'').toLowerCase(); return t.includes('pass')||t.includes('carry')||t.includes('dribble')||t.includes('cross')||t.includes('shot'); }
function dist(a,b){ return Math.hypot((a.ex-a.x)-(b.x-b.x)+ (a.ey-a.y)-(b.y-b.y)); } // simple hop distance at endpoints
function normalize(d){
  const {x,y,ex,ey}=scaleTo120x80(d);
  const away=((d.team||'home')+'').toLowerCase()==='away';
  const color=getComputedStyle(document.documentElement).getPropertyValue(away?'--away':'--home').trim();
  return { minute:+(d.minute||0), second:+(d.second||0), player:(d.player||''), team:(d.team||'home'), event:(d.event||'event'), x,y,ex,ey, xg:+(d.xg||0), color };
}

function clean(events){
  // 1) normalize + keep on-ball only if requested
  let evs = events.map(normalize);
  if ($('#onlyOnBall').checked) evs = evs.filter(isOnBall);
  // 2) drop micro-hops
  const MIN = Math.max(0, +($('#mind').value||3));
  const out=[]; let last=null;
  evs.forEach(e=>{
    if(!last){ out.push(e); last=e; return; }
    const d = Math.hypot(e.x - last.ex, e.y - last.ey);
    if(d >= MIN){ out.push(e); last=e; }
  });
  return out.map((e,i)=>({...e, step:i+1}));
}

function zoomThirdX(x){ // map x in [80..120] -> [0..120]
  if (x <= 80) return 0;
  if (x >= 120) return 120;
  return (x-80) * 3;
}

function draw(data){
  drawPitch();
  const group=n('g'); pitch.appendChild(group);

  let evs = clean(data);
  if ($('#flip').checked) evs = evs.map(e=>({...e, x:flipX(e.x), ex:flipX(e.ex)}));
  if ($('#finalThird').checked) evs = evs.map(e=>({...e, x:zoomThirdX(e.x), ex:zoomThirdX(e.ex)}));

  // path through starts -> final end
  if ($('#showPath').checked && evs.length){
    const pts = evs.map(e=>`${e.x},${e.y}`).join(' ') + ` ${evs.at(-1).ex},${evs.at(-1).ey}`;
    const pl=n('polyline'); pl.setAttribute('points',pts); pl.setAttribute('fill','none'); pl.setAttribute('stroke','#9aa5b5'); pl.setAttribute('opacity','.55'); pl.setAttribute('stroke-width','2'); pitch.appendChild(pl);
  }

  // per-event arrows + markers
  let cum=0;
  evs.forEach(e=>{
    arrow(group,e.x,e.y,e.ex,e.ey,e.color,1.6,.9);
    const r = 2.8 + 7*Math.sqrt(Math.min(e.xg,1));
    circle(group,e.ex,e.ey,r,e.color,.92);
    if ($('#numberSteps').checked) text(group,e.ex,e.ey,e.step,'#0b0d10',8.5);
    cum += e.xg;
  });

  // highlight final shot (ring)
  const last = evs.at(-1);
  if (last && last.event.toLowerCase().includes('shot')) ring(group,last.ex,last.ey,(3.2 + 7*Math.sqrt(Math.min(last.xg,1))), '#f8cc4a', 2);

  // KPI
  kpi.textContent = 'Cumulative xG: ' + cum.toFixed(2);
  msg.textContent = 'Loaded ' + data.length + ' events (' + evs.length + ' on-ball)';

  // timeline
  tl.innerHTML = evs.map(e=>(
    `<li data-step="${e.step}">
       <span class="badge">#${e.step}</span>
       <span class="type">${e.minute}:${String(e.second).padStart(2,'0')} • ${e.event}</span>
       <span class="ply">– ${e.player||''}</span>
       <span style="margin-left:auto">${e.xg?('xG '+e.xg.toFixed(2)):'&nbsp;'}</span>
     </li>`
  )).join('');

  // hover highlight sync
  const circles = Array.from(pitch.querySelectorAll('circle'));
  tl.querySelectorAll('li').forEach((li,idx)=>{
    li.onmouseenter=()=>{ circles[idx]?.setAttribute('opacity','1'); circles[idx]?.setAttribute('r', (parseFloat(circles[idx].getAttribute('r'))+1).toString()); };
    li.onmouseleave=()=>{ circles[idx]?.setAttribute('opacity','.92'); circles[idx]?.setAttribute('r', (parseFloat(circles[idx].getAttribute('r'))-1).toString()); };
  });
}

async function load(){
  try{
    const r = await fetch('/sequence.json?ts=' + Date.now());
    const text = await r.text(); let data;
    try{ data = JSON.parse(text); }catch(e){ msg.textContent='JSON parse error: '+e.message; return; }
    if(!Array.isArray(data)){ msg.textContent='Expected an array, got '+typeof data; return; }
    draw(data);
  }catch(e){ msg.textContent='Load error: '+e.message; }
}

$('#reload').onclick=load; [chkOnBall,chkNums,chkPath,chkFlip,chkThird,minDistInput].forEach(el=>el.addEventListener('change',load));
load();
</script>
</body></html>
""", mimetype="text/html")



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
