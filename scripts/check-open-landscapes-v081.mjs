import {Terrain,LAYOUTS} from '../site/engine.js';
const results={};
for(const layout of LAYOUTS){
 let totalSites=0,minSites=1e9,minCoverage=1,goodCoverage=0;
 for(let seed=1;seed<=30;seed++){
  const t=new Terrain(seed,'jungle',layout.id,4,{w:2000,h:900,water:825});
  const sites=t.spawnSites(); totalSites+=sites.length; minSites=Math.min(minSites,sites.length);
  const bins=new Set(sites.map(p=>Math.floor(p.x/20)));
  const coverage=bins.size/(2000/20); minCoverage=Math.min(minCoverage,coverage);
  if(coverage>=.14)goodCoverage++;
 }
 results[layout.id]={minSites,avgSites:Math.round(totalSites/30),minPlayableWidthPct:Math.round(minCoverage*100),seedsAbove14Pct:goodCoverage};
 if(minSites<12)throw new Error(layout.id+' has too few naturally playable sites: '+minSites);
 if(goodCoverage<24)throw new Error(layout.id+' has insufficient playable horizontal coverage: '+goodCoverage+'/30');
}
console.log(JSON.stringify({maps:LAYOUTS.length*30,results,status:'pass'},null,2));
