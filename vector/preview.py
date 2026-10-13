import math, sys, geopandas as gpd, pyogrio, shapely
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyproj import Transformer
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np
def tile2ll(x,y,z):
    n=2**z; return x/n*360-180, math.degrees(math.atan(math.sinh(math.pi*(1-2*y/n))))
z,x,y=16,34282,22921
w,n=tile2ll(x-1,y-1,z); e,s=tile2ll(x+2,y+2,z)
T=Transformer.from_crs(4326,2056,always_xy=True)
x0,y0=T.transform(w,s); x1,y1=T.transform(e,n)
bb=(x0,y0,x1,y1)
def rd(name): return pyogrio.read_dataframe(f"shp/swissTLM3D_TLM_{name}.shp",bbox=bb)
fig=plt.figure(figsize=(7.68,7.68),dpi=100); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.axis("off"); ax.set_facecolor("#FFFFFF")
px=(x1-x0)/768.0  # m pro Pixel
def poly(df,col,z=1):
    for g in df.geometry:
        if g is None: continue
        g=shapely.force_2d(g)
        for p in (g.geoms if g.geom_type.startswith("Multi") else [g]):
            verts=[];codes=[]
            for r in [p.exterior]+list(p.interiors):
                c=np.array(r.coords); verts+=list(c); codes+=[Path.MOVETO]+[Path.LINETO]*(len(c)-2)+[Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts,codes),fc=col,ec="none",zorder=z))
def line(df,col,lw,z,ls="-",cas=None,clw=0):
    for g in df.geometry:
        if g is None: continue
        g=shapely.force_2d(g)
        for l in (g.geoms if g.geom_type.startswith("Multi") else [g]):
            c=np.array(l.coords)
            if cas: ax.plot(c[:,0],c[:,1],color=cas,lw=clw,solid_capstyle="butt",zorder=z)
            ax.plot(c[:,0],c[:,1],color=col,lw=lw,ls=ls,solid_capstyle="butt",zorder=z+0.1)
bb_=pd=None
for nme in ["NUTZUNGSAREAL","VERKEHRSAREAL"]: poly(rd(nme),"#ECECE4",1)
b=rd("BODENBEDECKUNG_OST")
poly(b[b.OBJEKTART.isin(["Wald","Wald offen","Gebueschwald"])],"#C9E3B2",2)
poly(b[b.OBJEKTART=="Gehoelzflaeche"],"#DCECC8",2)
poly(b[b.OBJEKTART.isin(["Fels","Fels locker"])],"#D2D2CC",3)
poly(b[b.OBJEKTART=="Lockergestein"],"#E4E2D6",3)
poly(b[b.OBJEKTART=="Feuchtgebiet"],"#CFE6DA",3)
poly(b[b.OBJEKTART.isin(["Stehende Gewaesser","Fliessgewaesser"])],"#A9D3F2",4)
poly(rd("STEHENDES_GEWAESSER"),"#A9D3F2",4)
f=rd("FLIESSGEWAESSER"); line(f[(f.OBJEKTART=="Fliessgewaesser")&(f.STUFE=="0")],"#4FA3E0",1.2,5)
s=rd("STRASSE"); lw=lambda m: m*0.72/ (px/1.6) /1.0
sc=1.0
def road(sel,fill,w,cas=True,z=6):
    line(s[sel],fill,w*sc,z,cas="#000000" if cas else None,clw=(w+2)*sc)
t=s.OBJEKTART
road(t=="Autobahn","#F26B2D",7,z=9)
road(t.isin(["10m Strasse","8m Strasse"]),"#FFC81E",6,z=8)
road(t=="6m Strasse","#FFE57A",5,z=7)
road(t.isin(["4m Strasse","3m Strasse","Verbindung","Dienstzufahrt","Zufahrt","Ausfahrt","Einfahrt","Platz"]),"#FFFFFF",4,z=6)
w2=t.isin(["1m Weg","2m Weg"])
line(s[w2&(s.WANDERWEGE=="Wanderweg")],"#FFD400",3,5)
line(s[w2&(s.WANDERWEGE=="Wanderweg")],"#000000",1,5.5,ls=(0,(4,2)))
line(s[w2&(s.WANDERWEGE=="Bergwanderweg")],"#E60000",3,5)
line(s[w2&(s.WANDERWEGE=="Bergwanderweg")],"#000000",1,5.5,ls=(0,(4,2)))
line(s[w2&s.WANDERWEGE.isna()],"#000000",1,5,ls=(0,(4,3)))
e_=rd("EISENBAHN"); line(e_,"#000000",3,7,cas=None); line(e_,"#FFFFFF",1,7.2,ls=(0,(4,4)))
poly(pyogrio.read_dataframe("shp/swissTLM3D_TLM_GEBAEUDE_FOOTPRINT_OST.shp",bbox=bb),"#1C1C1C",10)
for nm,ty,fs in [("SIEDLUNGSNAME","Ort",16),]:
    d=rd(nm)
    for r in d.itertuples():
        if r.OBJEKTART==ty and r.NAME:
            p=shapely.force_2d(r.geometry).representative_point(); ax.text(p.x,p.y,r.NAME,fontsize=fs*0.6,ha="center",style="italic",zorder=20)
fig.savefig(sys.argv[1]); print("ok")
