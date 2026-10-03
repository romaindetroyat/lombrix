import {readFile,writeFile,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const version='0.5.2';
for(const f of await readdir('site'))if(/\.(js|html|css|webmanifest)$/.test(f)){
 const p='site/'+f;await writeFile(p,(await readFile(p,'utf8')).replaceAll('0.5.1',version));
}
await writeFile('solo.html',(await readFile('solo.html','utf8')).replaceAll('0.5.1',version));
const p=JSON.parse(await readFile('package.json','utf8'));p.name='lombrix';p.version=version;p.private=true;p.type='module';
p.scripts={test:'node --test *.test.mjs',dev:'wrangler dev',deploy:'wrangler deploy','test:live':'python3 check-live.py'};
await writeFile('package.json',JSON.stringify(p,null,2)+'\n');
const l=JSON.parse(await readFile('package-lock.json','utf8'));l.name=p.name;l.version=version;if(l.packages?.[''])Object.assign(l.packages[''],{name:p.name,version});await writeFile('package-lock.json',JSON.stringify(l,null,2)+'\n');
const cfg=JSON.parse(await readFile('wrangler.jsonc','utf8'));cfg.name='lombrix';cfg.compatibility_date='2026-10-03';await writeFile('wrangler.jsonc',JSON.stringify(cfg,null,2)+'\n');
await writeFile('site/_headers','/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n  X-Frame-Options: DENY\n/sw.js\n  Cache-Control: no-cache\n');
const hashes={};for(const f of [...(await readdir('site')).filter(f=>/\.(js|html|css|webmanifest)$/.test(f)).map(f=>'site/'+f),'core.mjs','worker.mjs','solo.html'])hashes[f]=createHash('sha256').update(await readFile(f)).digest('hex');
await writeFile('BUILD.json',JSON.stringify({version,repository:'romaindetroyat/lombrix',files:hashes},null,2)+'\n');
console.log('Prepared LOMBRIX '+version+' in dedicated repository.');
