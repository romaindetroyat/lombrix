"""LOMBRIX 0.8 terrain playability migration. Deterministic, repository-local."""
from pathlib import Path
p=Path("site/engine.js")
s=p.read_text()
repls=[
("const automatic=Math.round(clamp(1240+60*total,1360,3200)/80)*80;",
 "const automatic=Math.round(clamp(1500+85*total,1760,3200)/80)*80;"),
("fixed>=1360&&fixed<=3200&&fixed%80===0","fixed>=1760&&fixed<=3200&&fixed%80===0"),
("+m[5]<1360||+m[5]>3200","+m[5]<1760||+m[5]>3200"),
("+o.worldWidth>=1360&&+o.worldWidth<=3200","+o.worldWidth>=1760&&+o.worldWidth<=3200"),
("const minSpace=this.options.generation===4?58:36;","const minSpace=this.options.generation===4?72:36;"),
("let valid=sites.filter(p=>this.worms.every(w=>Math.hypot(w.x-p.x,w.y-p.y)>=minSpace));","let valid=sites.filter(p=>this.worms.every(w=>Math.hypot(w.x-p.x,w.y-p.y)>=minSpace&&Math.abs(w.x-p.x)>=72));"),
]
for old,new in repls:
    if old not in s: raise SystemExit("missing: "+old)
    s=s.replace(old,new)
old="""  /** Emplacements candidats : dégagement, pente et hauteur sûrs avant placement. */
  spawnSites(water=this.world.water) {
    const sites=[];
    for(let x=34;x<this.world.w-34;x+=4)for(let y=135;y<water-44;y++){
      if(!this.solid(x,y)||!this.solid(x,y+1)||!this.solid(x,y+4)||this.solid(x,y-1)||this.solid(x,y-32))continue;
      if(Math.abs(this.surface(x-9,y-11)-y)>10||Math.abs(this.surface(x+9,y-11)-y)>10)continue;
      if(this.solid(x-10,y-18)||this.solid(x+10,y-18))continue;
      let clear=true;for(let h=2;h<32;h++)if(this.solid(x,y-h)){clear=false;break;}if(!clear)continue;
      sites.push({x,y:y-1});
    }
    return sites;
  }"""
new="""  /** Emplacements candidats : une vraie zone jouable, pas seulement la place du corps.
   *  Le ver doit pouvoir se tenir debout, sauter et marcher de part et d'autre sans
   *  heurter immédiatement une voûte, une anfractuosité ou une plateforme suspendue. */
  spawnSites(water=this.world.water) {
    const sites=[];
    for(let x=52;x<this.world.w-52;x+=4)for(let y=135;y<water-44;y++){
      if(!this.solid(x,y)||!this.solid(x,y+1)||!this.solid(x,y+4)||this.solid(x,y-1))continue;
      let clear=true;
      for(let dx=-22;dx<=22&&clear;dx+=11)for(let h=2;h<=96;h+=3)if(this.solid(x+dx,y-h)){clear=false;break;}
      if(!clear)continue;
      const left=this.surface(x-28,y-18),right=this.surface(x+28,y-18);
      if(Math.abs(left-y)>14||Math.abs(right-y)>14)continue;
      if(this.solid(x-30,y-18)||this.solid(x+30,y-18)||this.solid(x-30,y-34)||this.solid(x+30,y-34))continue;
      sites.push({x,y:y-1});
    }
    return sites;
  }
  /** Dernier garde-fou après choix du spawn : libère le volume de saut et crée
   *  un petit palier marchable. Ne touche qu'au terrain initial, jamais aux cratères. */
  makeSpawnPlayable(x,y){
    const w=this.world.w,h=this.world.h;
    for(let yy=Math.max(0,Math.floor(y-104));yy<Math.max(0,Math.floor(y));yy++){
      const a=yy*w+Math.max(0,Math.floor(x-25)),b=yy*w+Math.min(w,Math.ceil(x+26));this.data.fill(0,a,b);
    }
    for(let yy=Math.max(0,Math.floor(y));yy<Math.min(h,Math.floor(y+10));yy++){
      const a=yy*w+Math.max(0,Math.floor(x-34)),b=yy*w+Math.min(w,Math.ceil(x+35));this.data.fill(1,a,b);
    }
  }"""
if old not in s: raise SystemExit("spawn block missing")
s=s.replace(old,new)
old2="""      const {x,y}=p;
      this.worms.push({id:this.worms.length,team,name:labels[team][i],x,y,vx:0,vy:0,hp:this.options.hp,maxHp:this.options.hp,dir:x<this.world.w/2?1:-1,grounded:true,input:0,inputTTL:0,energy:230,frozen:0,fallFrom:0});"""
new2="""      const {x,y}=p;
      this.terrain.makeSpawnPlayable(x,y);
      this.worms.push({id:this.worms.length,team,name:labels[team][i],x,y,vx:0,vy:0,hp:this.options.hp,maxHp:this.options.hp,dir:x<this.world.w/2?1:-1,grounded:true,input:0,inputTTL:0,energy:230,frozen:0,fallFrom:0});"""
if old2 not in s: raise SystemExit("placement block missing")
s=s.replace(old2,new2)
s=s.replace("export const VERSION = '0.7.0';","export const VERSION = '0.8.0';")
p.write_text(s)
print("terrain migration applied")
