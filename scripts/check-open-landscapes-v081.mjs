import {Terrain,LAYOUTS} from '../site/engine.js';
const results={};
for(const layout of LAYOUTS){
 let totalSites=0,minSites=1e9,longRuns=0,samples=0;
 for(let seed=1;seed<=30;seed++){
  const t=new Terrain(seed,'jungle',layout.id,4,{w:2000,h:900,water:825});
  const sites=t.spawnSites(); totalSites+=sites.length; minSites=Math.min(minSites,sites.length);
  const xs=new Set(sites.map(p=>Math.round(p.x/12)*12));
  let run=0,best=0,prev=null;
  for(const x of [...xs].sort((a,b)=>a-b)){if(prev!==null&&x-prev<=24)run++;else run=1;best=Math.max(best,run);prev=x;}
  if(best*12>=150)longRuns++; samples++;
 }
 results[layout.id]={minSites,avgSites:Math.round(totalSites/30),seedsWith150Run:longRuns};
 if(minSites<12)throw new Error(layout.id+' has too few naturally playable sites: '+minSites);
 if(longRuns<20)throw new Error(layout.id+' lacks broad playable runs: '+longRuns+'/30');
}
console.log(JSON.stringify({maps:LAYOUTS.length*30,results,status:'pass'},null,2));
