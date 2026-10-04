import test from 'node:test';
import assert from 'node:assert/strict';
import * as ui from './site/interaction.js';
import {WEAPONS,byWeapon} from './site/engine.js';
const view={width:844,height:390,worldWidth:3200};
const start={camera:{x:1100,y:450},scale:.5,zoom:1,x:560,y:210,distance:160};
const anchor=(v,p,viewport=view)=>({x:v.camera.x+(p.x-viewport.width/2)/v.scale,y:v.camera.y+(p.y-viewport.height/2)/v.scale});

test('pincement : le point du décor entre les doigts reste ancré hors centre',()=>{
 assert.equal(typeof ui.pinchView,'function');
 const before=anchor(start,start);
 const next=ui.pinchView(start,{x:560,y:210,distance:260},view);
 const after=anchor(next,{x:560,y:210});
 assert.ok(Math.abs(before.x-after.x)<1e-9);assert.ok(Math.abs(before.y-after.y)<1e-9);
 assert.equal(next.zoom,1.625);
});
test('pincement : translation et zoom combinés ne dérivent pas',()=>{
 const before=anchor(start,start);const mid={x:610,y:170,distance:240};const next=ui.pinchView(start,mid,view);const after=anchor(next,mid);
 assert.ok(Math.hypot(after.x-before.x,after.y-before.y)<1e-8);
 assert.deepEqual(start.camera,{x:1100,y:450});
});
test('pincement : aucune variation et limites de zoom stables',()=>{
 const same=ui.pinchView(start,start,view);assert.equal(same.zoom,start.zoom);assert.deepEqual(same.camera,start.camera);
 assert.equal(ui.pinchView(start,{...start,distance:1000},view).zoom,2.6);
 assert.equal(ui.pinchView(start,{...start,distance:1},view).zoom,.5);
});
test('pincement : bornes de caméra aux extrémités et terrain entièrement visible',()=>{
 const next=ui.pinchView({...start,camera:{x:100,y:450}}, {...start,x:820,distance:160},view);
 assert.equal(next.camera.x,view.width/next.scale/2);
 const all=ui.pinchView(start,{...start,distance:80},{...view,worldWidth:1360});assert.equal(all.camera.x,680);
});
test('commandes contextuelles : toutes les armes ont un verbe et des capacités explicites',()=>{
 assert.equal(typeof ui.weaponControls,'function');
 for(const def of WEAPONS){const p=ui.weaponControls(def);assert.equal(typeof p.action,'string');assert.ok(p.action.length<=12);assert.equal(p.power,Boolean(def.speed));assert.equal(p.target,Boolean(def.target));}
});
test('commandes contextuelles : soin, mine et cibles ne prétendent pas régler une puissance',()=>{
 for(const id of ['heal','mine','airstrike','teleport']){const p=ui.weaponControls(byWeapon[id]);assert.equal(p.power,false);assert.equal(p.angle,false);}
 assert.equal(ui.weaponControls(byWeapon.heal).action,'SOIGNER');assert.equal(ui.weaponControls(byWeapon.teleport).action,'TÉLÉPORTER');
 assert.equal(ui.weaponControls(byWeapon.dynamite).action,'POSER');
});
test('commandes contextuelles : précision et directions gardent leur angle sans fausse charge',()=>{
 for(const id of ['laser','shotgun','punch','bridge','dynamite']){const p=ui.weaponControls(byWeapon[id]);assert.equal(p.angle,true);assert.equal(p.power,false);}
 assert.equal(ui.weaponControls(byWeapon.rocket).angle,true);assert.equal(ui.weaponControls(byWeapon.rocket).power,true);
});

// Imported only after the camera step has been kept as an independent checkpoint.
const {alphaBounds}=await import('./site/render-cache.js');
function pixels(w,h,points){const a=new Uint8ClampedArray(w*h*4);for(const [x,y,alpha=255] of points)a[(y*w+x)*4+3]=alpha;return a;}
test('cache graphique : surface vide libérée au lieu de stocker du transparent',()=>{
 assert.equal(alphaBounds(pixels(20,12,[]),20,12),null);
});
test('cache graphique : rognage conservatif, antialias alpha faible conservé',()=>{
 assert.deepEqual(alphaBounds(pixels(20,12,[[6,5],[8,7,1]]),20,12),{x:4,y:3,width:7,height:7});
});
test('cache graphique : bordures clampées et surface opaque intacte',()=>{
 const a=new Uint8ClampedArray(8*9*4).fill(255);assert.deepEqual(alphaBounds(a,8,9),{x:0,y:0,width:8,height:9});
 assert.deepEqual(alphaBounds(pixels(8,9,[[0,0]]),8,9),{x:0,y:0,width:3,height:3});
});
test('cache graphique : dimensions incohérentes refusées',()=>{
 assert.throws(()=>alphaBounds(new Uint8Array(4),8,9),TypeError);
 assert.throws(()=>alphaBounds(new Uint8Array(40),0,9),TypeError);
});
