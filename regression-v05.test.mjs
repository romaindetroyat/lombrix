import test from 'node:test';
import assert from 'node:assert/strict';
import {powerFromPull,pullFromPower,dragPower,cameraRailMetrics,wormActing} from './site/interaction.js';
import {Game} from './site/engine.js';
test('charge tactile : poser le doigt loin ne saute jamais à 100 %',()=>{
 for(const power of [.04,.25,.5,.8,1])for(const d of [0,40,170,700])assert.ok(Math.abs(dragPower(power,d,d)-power)<1e-10);
});
test('charge tactile : davantage de course utile, 120 pixels depuis 50 % restent sous 85 %',()=>{
 assert.ok(dragPower(.5,100,220,546)<.85);assert.ok(dragPower(.5,100,160,546)>.5);
 assert.ok(dragPower(.5,100,60,546)<.5);
});
test('charge tactile : courbe monotone et bornée, aller-retour précis',()=>{
 let old=.04;for(let d=0;d<=540;d+=2){const p=powerFromPull(d);assert.ok(p>=old&&p<=1);assert.ok(Math.abs(pullFromPower(p)-d)<1e-8);old=p;}
 assert.equal(powerFromPull(-100),.04);assert.equal(powerFromPull(900),1);
});
test('charge tactile : plusieurs reprises du geste atteignent la pleine puissance',()=>{
 let power=.04;for(let i=0;i<8;i++)power=dragPower(power,80,160,540);assert.equal(power,1);
 for(let i=0;i<8;i++)power=dragPower(power,160,80,540);assert.equal(power,.04);
});
test('rail de caméra : les extrémités correspondent aux bornes visibles sans zoom',()=>{
 const m=cameraRailMetrics(3200,844,.475);assert.ok(Math.abs(m.min-m.fraction*1600)<1e-6);assert.ok(Math.abs(m.max+m.min-3200)<1e-6);assert.ok(m.span>1400);
 const all=cameraRailMetrics(1360,844,.5);assert.equal(all.span,0);assert.equal(all.fraction,1);
});
test('mimiques : personnalités indépendantes, pas de modification de l’état partagé',()=>{
 const w={id:5,team:1,hp:100,grounded:true,input:0};const before=structuredClone(w),acts=new Set();
 for(let t=0;t<16;t+=.1)acts.add(wormActing(w,t).mode);assert.ok(acts.size>=2);assert.deepEqual(w,before);
 assert.notEqual(wormActing(w,1).personality,wormActing({...w,id:6},1).personality);
});
test('mimiques : chute et dommage prioritaires, mouvements réduits respectés',()=>{
 assert.equal(wormActing({id:1,grounded:false},5).mode,'fall');assert.equal(wormActing({id:1,grounded:true},5,{hurt:.7}).mode,'hurt');
 const a=wormActing({id:2,grounded:true,input:1},10,{reduced:true});assert.equal(a.gesture,0);assert.equal(a.bob,0);assert.equal(a.crawl,0);
});
test('décès : identifiant, équipe et heure serveur, émission unique même après redégât',()=>{
 const g=new Game({seed:15,worms:2}),w=g.active();g.damage(w,1000);g.damage(w,1000);
 const deaths=g.events.filter(e=>e.type==='death');assert.equal(deaths.length,1);assert.equal(deaths[0].wormId,w.id);assert.equal(deaths[0].team,w.team);assert.equal(deaths[0].reason,'impact');assert.ok(Number.isFinite(deaths[0].at));
});
test('noyade : animation distincte et état de mort reproductible après restauration',()=>{
 const g=new Game({seed:15,worms:2}),w=g.active();w.y=g.water+9;w.grounded=false;g.tick();
 const e=g.events.find(e=>e.type==='death'&&e.wormId===w.id);assert.equal(e.reason,'water');assert.equal(e.y,g.water);
 const copy=Game.fromState(g.exportState());assert.deepEqual(copy.events,g.events);assert.equal(copy.worms.find(q=>q.id===w.id).hp,0);
});
