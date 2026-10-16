#!/usr/bin/env python3
"""Listet alle swissALTI3D-Kacheln (1 x 1 km, 2 m Aufloesung) mit dem neuesten Jahr je Kachel.

  python3 swissalti3d_kachelliste.py [ausgabe.json]      (ca. 15-20 Minuten, ca. 400 STAC-Seiten)

Ergebnis: JSON {"2665-1259": [2021, "https://data.geo.admin.ch/.../..._2_2056_5728.tif"], ...}
Der Kachelname ist die untere linke Ecke in LV95-Kilometern (E-N).
"""
import json, urllib.request, sys, re
url="https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissalti3d/items?limit=100"
best={}  # kachel -> (jahr, href)
n=0
while url:
    for attempt in range(5):
        try:
            d=json.load(urllib.request.urlopen(url, timeout=60)); break
        except Exception as e:
            if attempt==4: raise
    for f in d['features']:
        m=re.match(r'swissalti3d_(\d{4})_(\d{4}-\d{4})',f['id'])
        if not m: continue
        y,t=int(m.group(1)),m.group(2)
        href=next((a['href'] for k,a in f['assets'].items() if k.endswith('_2_2056_5728.tif')),None)
        if href and (t not in best or best[t][0]<y): best[t]=(y,href)
        n+=1
    url=next((l['href'] for l in d['links'] if l['rel']=='next'),None)
    if n%5000<100: print(n,len(best),flush=True)
json.dump(best,open(sys.argv[1] if len(sys.argv)>1 else 'tiles_2m.json','w'))
import collections
print("Items",n,"Kacheln",len(best),dict(collections.Counter(v[0] for v in best.values())))
