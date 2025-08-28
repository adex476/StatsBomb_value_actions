import json
d=json.load(open('sequence.json','r',encoding='utf-8'))
print("items:", len(d))
print("sum_xg:", sum(float(e.get('xg') or 0) for e in d))
last = d[-1] if d else{}
print("last event:", last.get('event'), 'xg:', last.get("xg"))
print("first 3:", [{k:ev.get(k) for k in ("event", 'x', 'y', 'end_x', 'end_y', 'xg')} for ev in d[:3]])
