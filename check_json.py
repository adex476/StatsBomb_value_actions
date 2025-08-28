# Check_json .py

import json, math
with open("sequence.json", "r", encoding='utf-8') as f: data = json.load(f)
print(type(data).__name__, "length:", (len(data) if isinstance(data,list) else "n/a"))
bad=0
if isinstance(data,list):
    for i,e in enumerate(data):
        for k in ("x","y","end_x","end_y","xg"):
            v = e.get(k,0)
            if v is None or (isinstance(v,(int,float)) and (math.isnan(v) or math.isinf(v))):
                bad+=1; break
    print("bad numeric entries:", bad)
    if data: print("first keys:", list(data[0].keys()))