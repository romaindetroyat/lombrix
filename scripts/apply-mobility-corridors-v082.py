"""LOMBRIX 0.8.2: guarantee spawn mobility corridors."""
from pathlib import Path
p=Path("site/engine.js");s=p.read_text()
old="""      const left=this.surface(x-28,y-18),right=this.surface(x+28,y-18);
      if(Math.abs(left-y)>14||Math.abs(right-y)>14)continue;
      if(this.solid(x-30,y-18)||this.solid(x+30,y-18)||this.solid(x-30,y-34)||this.solid(x+30,y-34))continue;
      sites.push({x,y:y-1});"""
new="""      const corridor=dir=>{
        for(let d=18;d<=92;d+=6){
          const px=x+dir*d,ground=this.surface(px,y-20);
          if(Math.abs(ground-y)>16)return false;
          for(let h=8;h<=54;h+=8)if(this.solid(px,y-h))return false;
        }
        return true;
      };
      const left=corridor(-1),right=corridor(1);
      // Au moins un vrai couloir de marche; les deux côtés sont fortement préférés.
      if(!left&&!right)continue;
      sites.push({x,y:y-1,leftOpen:left,rightOpen:right,mobility:(left?1:0)+(right?1:0)});"""
if old not in s: raise SystemExit("spawn fragment missing")
s=s.replace(old,new)
old2="""      valid.sort((a,b)=>(Math.abs(a.x-target)+Math.abs(a.y-preferredY)*.24)-(Math.abs(b.x-target)+Math.abs(b.y-preferredY)*.24)||a.y-b.y);"""
new2="""      valid.sort((a,b)=>((2-(b.mobility||0))*180+Math.abs(a.x-target)+Math.abs(a.y-preferredY)*.24)-((2-(a.mobility||0))*180+Math.abs(b.x-target)+Math.abs(b.y-preferredY)*.24)||a.y-b.y);"""
# Correct comparator explicitly after insertion to avoid sign ambiguity.
new2="""      valid.sort((a,b)=>{const sa=(2-(a.mobility||0))*180+Math.abs(a.x-target)+Math.abs(a.y-preferredY)*.24,sb=(2-(b.mobility||0))*180+Math.abs(b.x-target)+Math.abs(b.y-preferredY)*.24;return sa-sb||a.y-b.y;});"""
if old2 not in s: raise SystemExit("sort fragment missing")
s=s.replace(old2,new2)
old3="""  makeSpawnPlayable(x,y){
    const w=this.world.w,h=this.world.h;
    for(let yy=Math.max(0,Math.floor(y-104));yy<Math.max(0,Math.floor(y));yy++){
      const a=yy*w+Math.max(0,Math.floor(x-25)),b=yy*w+Math.min(w,Math.ceil(x+26));this.data.fill(0,a,b);
    }
    for(let yy=Math.max(0,Math.floor(y));yy<Math.min(h,Math.floor(y+10));yy++){
      const a=yy*w+Math.max(0,Math.floor(x-34)),b=yy*w+Math.min(w,Math.ceil(x+35));this.data.fill(1,a,b);
    }
  }"""
new3="""  makeSpawnPlayable(x,y){
    const w=this.world.w,h=this.world.h;
    // A 170-unit launch pad prevents a pillar or floating ledge from sitting directly
    // in front of a newly spawned worm. This is intentionally wider than its body.
    for(let yy=Math.max(0,Math.floor(y-104));yy<Math.max(0,Math.floor(y));yy++){
      const a=yy*w+Math.max(0,Math.floor(x-86)),b=yy*w+Math.min(w,Math.ceil(x+87));this.data.fill(0,a,b);
    }
    for(let yy=Math.max(0,Math.floor(y));yy<Math.min(h,Math.floor(y+10));yy++){
      const a=yy*w+Math.max(0,Math.floor(x-86)),b=yy*w+Math.min(w,Math.ceil(x+87));this.data.fill(1,a,b);
    }
  }"""
if old3 not in s: raise SystemExit("playable fragment missing")
s=s.replace(old3,new3)
p.write_text(s)
print("mobility corridors applied")
