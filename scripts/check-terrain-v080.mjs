import {Game,LAYOUTS} from './site/engine.js';
let maps=0,worms=0,minWidth=Infinity,maxWidth=0;
for(const layout of LAYOUTS)for(const count of [1,3,5,8])for(const teams of [2,4])for(let seed=1;seed<=10;seed++){
  const names=Array.from({length:teams},(_,i)=>'T'+i);
  const g=new Game({layout:layout.id,theme:'jungle',worms:count,seed,generation:4},names);
  maps++;minWidth=Math.min(minWidth,g.world.w);maxWidth=Math.max(maxWidth,g.world.w);
  if(g.world.w<1760)throw new Error('terrain too narrow '+g.world.w);
  for(const w of g.worms){worms++;
    if(!g.terrain.solid(w.x,w.y+2))throw new Error('no support '+layout.id);
    for(const dx of [-22,-11,0,11,22])for(let h=6;h<=92;h+=6)
      if(g.terrain.solid(w.x+dx,w.y-h))throw new Error('spawn ceiling '+layout.id+' '+seed);
    for(const dx of [-28,28]){
      const sy=g.terrain.surface(w.x+dx,w.y-18);
      if(Math.abs(sy-(w.y+1))>16)throw new Error('spawn pocket '+layout.id+' '+seed);
    }
  }
}
console.log(JSON.stringify({maps,worms,minWidth,maxWidth,status:'pass'}));
