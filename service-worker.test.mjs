import {test} from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const code=await readFile(new URL('./site/sw.js',import.meta.url),'utf8');
function harness({failAsset=false}={}) {
 const listeners={},stores=new Map();let offline=false,claimed=0,requests=0,skips=0;
 const key=x=>new URL(typeof x==='string'?x:x.url,'https://lombrix.test').href;
 const caches={async open(name){if(!stores.has(name))stores.set(name,new Map());const data=stores.get(name);return {async put(k,v){data.set(key(k),v.clone());},async match(k){return data.get(key(k))?.clone();}};},async keys(){return [...stores.keys()];},async delete(k){return stores.delete(k);}};
 class RequestWithBase extends Request {constructor(input,init){super(typeof input==='string'?key(input):input,init);}}
 const self={skipWaiting(){skips++;},location:{origin:'https://lombrix.test'},clients:{async claim(){claimed++;}},addEventListener(n,f){listeners[n]=f;}};
 const fetch=async req=>{requests++;if(offline)throw new Error('offline');if(failAsset&&key(req).includes('style.css'))return new Response('missing',{status:404});const html=new URL(req.url).pathname==='/';const r=new Response(html?'<html>LOMBRIX 0.5.2</html>':'asset',{headers:{'content-type':html?'text/html':'text/javascript','content-encoding':'gzip','location':'/'}});if(html)Object.defineProperty(r,'redirected',{value:true});return r;};
 vm.runInNewContext(code,{self,caches,fetch,Request:RequestWithBase,Response,Headers,URL,console});
 return {caches,setOffline(v){offline=v;},get requests(){return requests;},get skips(){return skips;},message(data){listeners.message({data});},get claimed(){return claimed;},async event(n){let p;listeners[n]({waitUntil(v){p=v;}});await p;},async request(path,mode='navigate',method='GET'){let p;listeners.fetch({request:{url:key(path),method,mode},respondWith(v){p=v;}});return p?await p:null;}};
}
test('Safari navigation uses decoded non-redirected HTML',async()=>{const h=harness();await h.event('install');const r=await h.request('/?room=ABC234');assert.equal(r.redirected,false);assert.equal(r.headers.get('content-encoding'),null);assert.equal(r.headers.get('location'),null);assert.match(await r.text(),/LOMBRIX/);});
test('Offline reload and invitation query keep the game shell available',async()=>{const h=harness();await h.event('install');h.setOffline(true);for(const path of ['/','/?room=ABC234','/index.html'])assert.equal((await h.request(path)).status,200);});
test('API calls never enter the game cache',async()=>{const h=harness();await h.event('install');const n=h.requests;assert.equal(await h.request('/api/rooms/ABC234','cors'),null);assert.equal(await h.request('/api/rooms','cors','POST'),null);assert.equal(await h.request('/health','cors'),null);assert.equal(h.requests,n);});
test('Failed precache rejects incomplete release',async()=>{const h=harness({failAsset:true});await assert.rejects(h.event('install'));assert.deepEqual(await h.caches.keys(),[]);});
test('Activation removes only obsolete LOMBRIX caches',async()=>{const h=harness();await h.caches.open('other-app');await h.caches.open('lombrix-old');await h.event('install');await h.event('activate');assert.equal(h.claimed,1);assert((await h.caches.keys()).includes('other-app'));assert(!(await h.caches.keys()).includes('lombrix-old'));assert.equal(h.skips,0);});

test('Updates activate only after the explicit idle UI request',async()=>{const h=harness();await h.event('install');assert.equal(h.skips,0);h.message({type:'other'});assert.equal(h.skips,0);h.message({type:'ACTIVATE_WHEN_IDLE'});assert.equal(h.skips,1);});
