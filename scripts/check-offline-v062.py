"""Real origin shutdown test, using unmodified deployed site files.
Playwright WebKit setOffline limitation: microsoft/playwright#42775.
This checks server unavailability, not physical iPhone airplane mode.
"""
import asyncio,json,threading,functools,http.server,time,datetime
from pathlib import Path
from playwright.async_api import async_playwright
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path=='/index.html':self.send_response(301);self.send_header('Location','/');self.end_headers();return
  super().do_GET()
async def main():
 results=[]
 async with async_playwright() as tool:
  for engine in ['webkit','chromium']:
   server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(Path('site').resolve())))
   origin='http://127.0.0.1:'+str(server.server_port)
   thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   stopped=False;browser=await getattr(tool,engine).launch(headless=True)
   ctx=await browser.new_context(viewport={'width':844,'height':390},is_mobile=True,has_touch=True)
   page=await ctx.new_page();page.set_default_timeout(20000)
   try:
    await page.goto(origin,wait_until='domcontentloaded')
    await page.wait_for_function("document.documentElement.dataset.lombrixReady==='true'")
    await page.evaluate('navigator.serviceWorker.ready');await page.wait_for_function('!!navigator.serviceWorker.controller')
    cached=await page.evaluate("async()=>{const c=await caches.open('lombrix-v0.6.2-r1');const r=await c.match('/index.html');return {present:!!r,redirected:r?.redirected};}")
    assert cached=={'present':True,'redirected':False},cached
    await asyncio.to_thread(server.shutdown);server.server_close();stopped=True
    # Negative control: a new uncached fetch must fail once the socket is closed.
    probe=await page.evaluate("async()=>{try{await fetch('/origin-unavailable-'+Date.now(),{cache:'no-store'});return false;}catch{return true;}}")
    assert probe,'Origin was not actually unavailable'
    r=await page.reload(wait_until='domcontentloaded')
    assert r.status==200;assert r.from_service_worker,'Navigation did not come from the service worker'
    await page.wait_for_function("document.documentElement.dataset.lombrixReady==='true'")
    await page.locator('#solo').tap();await page.locator('#battle').wait_for(state='visible');await page.wait_for_function('!document.querySelector("#fire").disabled')
    await page.locator('[data-loadout="heal"]').scroll_into_view_if_needed();await page.locator('[data-loadout="heal"]').tap();await page.locator('#fire').tap()
    await page.wait_for_function("document.querySelector('#round-info').textContent==='TOUR 3'",timeout=45000)
    await page.wait_for_function('!document.querySelector("#fire").disabled')
    results.append({'engine':engine,'status':'pass','negativeNetworkControl':True,'fromServiceWorker':True,'actionAndAIReturn':True})
   except Exception as e:results.append({'engine':engine,'status':'fail','error':str(e)})
   finally:
    if not stopped:await asyncio.to_thread(server.shutdown);server.server_close()
    await browser.close()
   Path('reports/v062/offline-origin-stopped.json').write_text(json.dumps({'version':'0.6.2','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Actual local HTTP origin stopped; identical site code; no browser offline emulation','physicalIPhone':False,'results':results},indent=2)+'\n')
   print(json.dumps(results[-1]),flush=True)
 if any(r['status']!='pass' for r in results):raise SystemExit(1)
asyncio.run(main())
