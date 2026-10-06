import {Game} from '../site/engine.js';
const layouts=['fortress','skylands','caverns','spires','bridges','terraces','ridge','archipelago','canyon','basin'];
let maps=0,worms=0,bilateral=0;
for(const layout of layouts)for(const count of [2,4,8])for(let seed=1;seed<=35;seed++){
 const g=new Game({layout,theme:'candy',worms:count,seed,generation:4},['A','B']);maps++;
 for(const w of g.worms){worms++;
  const open=dir=>{for(let d=20;d<=78;d+=6){const x=w.x+dir*d,sy=g.terrain.surface(x,w.y-20);if(Math.abs(sy-(w.y+1))>17)return false;for(let h=8;h<=50;h+=7)if(g.terrain.solid(x,w.y-h))return false;}return true;};
  const l=open(-1),r=open(1);if(!l&&!r)throw new Error('trapped '+layout+' seed '+seed+' worm '+w.id);
  if(l&&r)bilateral++;
 }
}
if(bilateral/worms<.88)throw new Error('too few bilateral spawns '+bilateral+'/'+worms);
console.log(JSON.stringify({maps,worms,bilateral,bilateralPct:Math.round(100*bilateral/worms),status:'pass'}));
