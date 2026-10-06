"""LOMBRIX 0.8.1: broader, less cluttered terrain silhouettes."""
from pathlib import Path
p=Path("site/engine.js");s=p.read_text()
repls={
"""      // Trois étages décalés : chaque graine redistribue largeur et altitude.
      for(let row=0;row<3;row++)for(let col=0;col<4;col++){
        const cx=165+col*385+(r()-.5)*82+(row%2)*30,cy=300+row*176+(r()-.5)*65;
        isle(cx,cy,104+r()*49,55+r()*76);
      }""":"""      // Deux niveaux seulement, avec de longues îles : on privilégie les courses et
      // les trajectoires lisibles aux petits morceaux de terrain empilés.
      for(let row=0;row<2;row++)for(let col=0;col<4;col++){
        const cx=150+col*430+(r()-.5)*48+(row%2)*45,cy=315+row*270+(r()-.5)*38;
        isle(cx,cy,145+r()*42,58+r()*55);
      }""",
"""      for(let i=0;i<2;i++)isle(480+i*620+(r()-.5)*120,245+r()*80,100+r()*35,60+r()*50);""":"""      isle(800+(r()-.5)*170,245+r()*55,155+r()*45,62+r()*38);""",
"""      for(let i=0;i<4;i++)isle(center+(i%2?1:-1)*(gap/2-48),510+Math.floor(i/2)*145,85+r()*40,60+r()*35);
      isle(center,270+r()*35,105+r()*40,75);""":"""      for(let side of [-1,1])isle(center+side*(gap/2-30),535+r()*55,135+r()*35,62+r()*28);
      isle(center,245+r()*30,145+r()*35,65);""",
"""      const n=5+Math.floor(r()*2),step=1480/n;""":"""      const n=4,step=1480/n;""",
"""        const cx=60+step*(i+.5),ww=130+r()*45,top=290+r()*210;""":"""        const cx=60+step*(i+.5),ww=185+r()*35,top=330+r()*145;""",
"""      const n=5,step=310,tops=[];""":"""      const n=4,step=400,tops=[];""",
"""      for(let i=0;i<n;i++){const cx=175+i*step,top=410+r()*110;tops.push([cx,top]);this.polygon([[cx-95,900],[cx-72,top+24],[cx-63,top],[cx+67,top+5],[cx+80,top+36],[cx+100,900]]);}""":"""      for(let i=0;i<n;i++){const cx=160+i*step,top=430+r()*85;tops.push([cx,top]);this.polygon([[cx-135,900],[cx-105,top+24],[cx-95,top],[cx+100,top+5],[cx+115,top+36],[cx+145,900]]);}""",
"""      isle(790,250,126,75);""":"""      // Le ciel reste volontairement libre : pas d'île basse au-dessus des ponts.""",
"""      for(let i=0;i<9;i++){const x=100+i*175+(r()-.5)*40,top=280+r()*320,ww=48+r()*20;this.polygon([[x-ww-30,810],[x-ww,top+20],[x-ww+10,top],[x+ww-10,top+3],[x+ww,top+28],[x+ww+40,810]]);}""":"""      for(let i=0;i<6;i++){const x=120+i*270+(r()-.5)*35,top=330+r()*245,ww=78+r()*24;this.polygon([[x-ww-42,810],[x-ww,top+20],[x-ww+10,top],[x+ww-10,top+3],[x+ww,top+28],[x+ww+48,810]]);}""",
"""      for(let i=0;i<4;i++)isle(180+i*390+(r()-.5)*80,275+r()*95,95+r()*65,70);""":"""      for(let i=0;i<2;i++)isle(360+i*820+(r()-.5)*70,255+r()*70,150+r()*55,65);""",
"""      isle(cx+(r()-.5)*200,365+r()*70,105+r()*45,85);""":"""      // Le centre du cirque reste ouvert pour les tirs et les déplacements.""",
"""      for(let i=0;i<7;i++){
        const cx=180+i*205,cy=500+(i%2)*108,rx=85+r()*24;""":"""      for(let i=0;i<5;i++){
        const cx=190+i*300,cy=535+(i%2)*105,rx=118+r()*28;""",
"""      for(let i=0;i<2+Math.floor(r()*2);i++)isle(390+i*390+(r()-.5)*90,245+r()*92,95+r()*55,70+r()*38);""":"""      for(let i=0;i<1+Math.floor(r()*2);i++)isle(500+i*650+(r()-.5)*70,220+r()*65,145+r()*45,62+r()*30);""",
"""    if(!['skylands','caverns','fortress','bridges'].includes(id))for(let i=0;i<6;i++){""":"""    if(!['skylands','caverns','fortress','bridges'].includes(id))for(let i=0;i<3;i++){""",
"""      const cx=140+r()*1320,cy=650+r()*125,rad=22+r()*30,pts=[];""":"""      const cx=170+r()*1260,cy=680+r()*90,rad=22+r()*24,pts=[];"""
}
for old,new in repls.items():
    if old not in s: raise SystemExit("missing terrain fragment: "+old[:70])
    s=s.replace(old,new)
p.write_text(s)
print("open landscape migration applied")
