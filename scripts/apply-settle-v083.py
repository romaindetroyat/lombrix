"""LOMBRIX 0.8.3: stop wall jitter and shorten post-impact settling."""
from pathlib import Path
p=Path("site/engine.js");s=p.read_text()
old="""      if(this.displace(w,requested,0,true)<.95){w.vx*=.15;w.driveVX=0;}
      w.vx*=Math.pow(w.grounded?.008:.55,dt);"""
new="""      const moved=this.displace(w,requested,0,true);
      if(moved<.95){w.vx*=.08;w.driveVX=0;}
      // Tiny residual wall velocity is numerical noise, not gameplay. Killing it
      // prevents alternating sub-pixel poses and lets the turn settle immediately.
      if(moved<.25&&Math.abs(w.vx)<34)w.vx=0;
      w.vx*=Math.pow(w.grounded?.004:.48,dt);
      if(w.grounded&&Math.abs(w.vx)<3)w.vx=0;"""
if old not in s: raise SystemExit("movement fragment missing")
s=s.replace(old,new)
old2="""    for(const w of bodies){w.vx=clamp(w.vx,-1200,1200);w.vy=clamp(w.vy,-1200,1300);}
  }
  step(dt,realDt) {"""
new2="""    for(const w of bodies){
      w.vx=clamp(w.vx,-1200,1200);w.vy=clamp(w.vy,-1200,1300);
      if(w.grounded&&Math.abs(w.vx)<3)w.vx=0;
      if(w.grounded&&Math.abs(w.vy)<3)w.vy=0;
    }
  }
  wormActuallyMoving(w){
    if(w.hp<=0)return false;
    // A grounded body pressed against terrain with tiny residual velocity is asleep.
    if(w.grounded&&Math.abs(w.vx)<6&&Math.abs(w.vy)<6)return false;
    return !w.grounded||Math.abs(w.vx)>=6||Math.abs(w.vy)>=6;
  }
  step(dt,realDt) {"""
if old2 not in s: raise SystemExit("contact fragment missing")
s=s.replace(old2,new2)
old3="""    if(this.phase==='flight'&&!this.projectiles.length&&this.retreat<=0){const moving=this.worms.some(w=>w.hp>0&&(!w.grounded||Math.abs(w.vx)>10));const ticking=this.mines.some(m=>m.trigger!==null);if(!moving&&!ticking)this.settle-=realDt;if(this.settle<=0||this.flightAge>18)this.nextTurn();}"""
new3="""    if(this.phase==='flight'&&!this.projectiles.length&&this.retreat<=0){
      const moving=this.worms.some(w=>this.wormActuallyMoving(w)),ticking=this.mines.some(m=>m.trigger!==null);
      if(!moving&&!ticking)this.settle-=realDt;
      else if(this.flightAge>2.8&&!ticking){
        // Do not hold the match hostage for a body rubbing indefinitely on a wall.
        const meaningful=this.worms.some(w=>w.hp>0&&(Math.abs(w.vx)>22||Math.abs(w.vy)>22));
        if(!meaningful)this.settle-=realDt*2.5;
      }
      if(this.settle<=0||this.flightAge>7)this.nextTurn();
    }"""
if old3 not in s: raise SystemExit("settle fragment missing")
s=s.replace(old3,new3)
p.write_text(s);print("settle patch applied")
