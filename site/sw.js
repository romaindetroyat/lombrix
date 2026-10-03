/* One coherent shell per release. Never replace the engine mid-match. */
const CACHE = 'lombrix-v0.5.2-r1';
const HTML_KEY = '/index.html';
const ASSETS = ['/style.css?v=0.5.2','/boot.js?v=0.5.2','/app.js?v=0.5.2','/engine.js?v=0.5.2','/interaction.js?v=0.5.2','/render-cache.js?v=0.5.2','/art.js?v=0.5.2','/renderer.js?v=0.5.2','/audio.js?v=0.5.2','/manifest.webmanifest','/assets/mascots.svg','/assets/icon.svg','/assets/icon-192.png','/assets/icon-512.png'];
async function cleanResponse(response) {
  if (!response.ok || response.type === 'opaque' || response.type === 'opaqueredirect') throw new Error('Invalid offline shell response');
  // Static hosts redirect /index.html to /. A redirected cached Response
  // cannot be used for some navigation modes, including Safari/WebKit reloads.
  const headers = new Headers(response.headers);
  for (const key of ['content-encoding','content-length','transfer-encoding','location']) headers.delete(key);
  return new Response(await response.arrayBuffer(), {status:response.status,statusText:response.statusText,headers});
}
self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    try {
      const html = await cleanResponse(await fetch(new Request('/', {cache:'reload',redirect:'follow'})));
      if (!(html.headers.get('content-type') || '').includes('text/html')) throw new Error('Missing game HTML');
      await cache.put(HTML_KEY, html);
      await Promise.all(ASSETS.map(async path => cache.put(path, await cleanResponse(await fetch(new Request(path, {cache:'reload',redirect:'follow'}))))));
    } catch (error) {await caches.delete(CACHE);throw error;}
  })());
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    await Promise.all((await caches.keys()).filter(k => k.startsWith('lombrix-') && k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  const u = new URL(event.request.url);
  if (event.request.method !== 'GET' || u.origin !== self.location.origin || u.pathname.startsWith('/api/') || u.pathname === '/health') return;
  if (event.request.mode === 'navigate') {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE);const cached = await cache.match(HTML_KEY);
      if (cached) return cleanResponse(cached);
      try {return await cleanResponse(await fetch(new Request('/', {redirect:'follow'})));}
      catch {return new Response('Le jeu doit etre charge une premiere fois avec Internet.', {status:503,headers:{'Content-Type':'text/plain;charset=utf-8'}});}
    })());return;
  }
  if (ASSETS.includes(u.pathname + u.search) || ASSETS.includes(u.pathname)) event.respondWith(caches.open(CACHE).then(async cache => (await cache.match(event.request)) || fetch(event.request)));
});
