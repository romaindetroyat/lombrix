import {Game} from '../site/engine.js';
function wallCase(seed=12){
 const g=new Game({layout:'fortress',theme:'candy',worms:2,seed,generation:4,pace:'lively'},['A','B']);
 const w=g.active();
 // Create a deterministic wall next to the active worm, then push it into it.
 g.terrain.rect(w.x+18,w.y-75,20,78,false);w.vx=26;w.grounded=true;g.phase='flight';g.projectiles=[];g.retreat=0;g.settle=.24;g.flightAge=0;
 let maxLateSpeed=0,changes=0,lastX=w.x,endAt=null;
 for(let i=0;i<600;i++){g.tick(1/60);if(i>30)maxLateSpeed=Math.max(maxLateSpeed,Math.abs(w.vx));if(Math.abs(w.x-lastX)>.05)changes++;lastX=w.x;if(g.phase==='aim'&&g.turn>0){endAt=i/60;break;}}
 if(endAt===null||endAt>3)throw new Error('wall settle too slow '+endAt);
 if(maxLateSpeed>6)throw new Error('wall jitter persists '+maxLateSpeed);
 return {endAt,changes,maxLateSpeed};
}
let worst=0,totalChanges=0;
for(let seed=1;seed<=120;seed++){const r=wallCase(seed);worst=Math.max(worst,r.endAt);totalChanges+=r.changes;}
console.log(JSON.stringify({cases:120,worstSeconds:worst,totalPositionChanges:totalChanges,status:'pass'}));
