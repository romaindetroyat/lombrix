import asyncio,json,traceback,os,datetime
from pathlib import Path
from playwright.async_api import async_playwright
OUT=Path('reports');OUT.mkdir(exist_ok=True)
URL=os.environ.get('LOMBRIX_URL') or json.loads((OUT/'deployment.json').read_text())['url']
results=[]
def record(engine,step,status,**extra):
 results.append(dict(engine=engine,step=step,status=status,**extra))
 (OUT/'browser.json').write_text(json.dumps({'url':URL,'version':'0.5.2','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results},indent=2)+'\n')
 print(engine,step,status,flush=True)
async def ready(p):
 await p.wait_for_function("document.documentElement.dataset.lombrixReady==='true'",timeout=30000)
async def go(p,url):
 r=await p.goto(url,wait_until='domcontentloaded',timeout=45000)
 assert r and r.status==200,'Game navigation not HTTP 200'
 await ready(p)
async def slider(p,selector,value):
 await p.locator(selector).evaluate('(el,v)=>{el.value=String(v);el.dispatchEvent(new Event("input",{bubbles:true}));}',value)
async def turn(p,number):
 await p.wait_for_function('(n)=>document.querySelector("#round-info").textContent==="TOUR "+n',arg=number,timeout=45000)
async def snapshot(p,code):
 return await p.evaluate("async c=>(await fetch('/api/rooms/'+c+'/sync?ops=0')).json()",code)
async def run():
 async with async_playwright() as tool:
  for engine in ['webkit','chromium']:
   browser=await getattr(tool,engine).launch(headless=True)
   options=dict(viewport={'width':844,'height':390},device_scale_factor=2,is_mobile=True,has_touch=True)
   ctx=await browser.new_context(**options);p=await ctx.new_page();p.set_default_timeout(18000)
   errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   try:
    await go(p,URL+'/');await p.locator('#solo').tap();await p.locator('#battle').wait_for(state='visible')
    await p.wait_for_function('!document.querySelector("#fire").disabled')
    await slider(p,'#angle',-55);await slider(p,'#power',35);await p.locator('#fire').tap()
    await turn(p,3);await p.wait_for_function('!document.querySelector("#fire").disabled')
    assert not errors,errors
    await p.screenshot(path=str(OUT/(engine+'-solo.png')))
    record(engine,'solo-start-real-shot-AI-return','pass')
   except Exception as e:record(engine,'solo-start-real-shot-AI-return','fail',error=str(e),pageErrors=errors)
   try:
    await p.evaluate('navigator.serviceWorker.ready');await p.wait_for_function('!!navigator.serviceWorker.controller',timeout=20000)
    await go(p,URL+'/');await p.reload(wait_until='domcontentloaded');await ready(p)
    record(engine,'reload-with-active-service-worker','pass')
    await ctx.set_offline(True);await p.reload(wait_until='domcontentloaded');await ready(p)
    await p.locator('#solo').tap();await p.locator('#battle').wait_for(state='visible');await p.wait_for_function('!document.querySelector("#fire").disabled')
    await p.locator('#arsenal').tap();await p.locator('[data-category="Utilitaires"]').tap();await p.locator('[data-weapon="heal"]').tap();await p.locator('#fire').tap();await turn(p,3)
    record(engine,'offline-solo-action-AI-return','pass')
   except Exception as e:record(engine,'offline-and-reload','fail',error=str(e))
   finally:await ctx.close()
   contexts=[];code=None
   try:
    contexts=[await browser.new_context(**options) for _ in range(2)]
    pages=[await c.new_page() for c in contexts];a,b=pages
    for p in pages:p.set_default_timeout(20000)
    for p in pages:await go(p,URL+'/')
    await a.locator('#nickname').fill('Alice recette');await a.locator('#create-duel').tap()
    await a.locator('#opt-worms').select_option('2');await a.locator('#opt-time').select_option('60')
    await a.locator('#confirm-config').tap();await a.locator('#lobby').wait_for(state='visible')
    code=(await a.locator('#room-code').inner_text()).strip()
    await b.evaluate('navigator.serviceWorker.ready');await b.wait_for_function('!!navigator.serviceWorker.controller')
    await go(b,URL+'/?room='+code);await b.locator('#join-name').fill('Bob recette');await b.locator('#join-submit').tap()
    await b.locator('#lobby').wait_for(state='visible');await b.locator('#ready').tap()
    await a.wait_for_function('!document.querySelector("#start-room").disabled');await a.locator('#start-room').tap()
    for p in pages:await p.locator('#battle').wait_for(state='visible')
    await a.wait_for_timeout(1500)
    active=a if await a.locator('#fire').is_enabled() else b;other=b if active==a else a
    assert await active.locator('#fire').is_enabled();assert not await other.locator('#fire').is_enabled()
    first=await snapshot(active,code);second=await snapshot(other,code)
    assert first['game']['key']==second['game']['key']
    assert first['game']['world']==second['game']['world']
    assert first['game']['worms']==second['game']['worms']
    bad=await other.evaluate("""async ({c,g})=>{const r=await fetch('/api/rooms/'+c+'/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({matchId:g.key,turn:g.turn,seq:987654321,command:{type:'fire',weapon:'rocket',angle:-0.5,power:0.5}})});return r.status;}""",dict(c=code,g=first['game']))
    assert bad in [403,409],'Opponent was allowed to command active team'
    await slider(active,'#angle',-55);await slider(active,'#power',35);await active.locator('#fire').tap()
    for p in pages:await turn(p,2)
    await other.wait_for_function('!document.querySelector("#fire").disabled')
    one=await snapshot(active,code);two=await snapshot(other,code)
    assert one['game']['ops']==two['game']['ops'],'Terrain differs after shot'
    assert [(w['id'],w['hp']) for w in one['game']['worms']]==[(w['id'],w['hp']) for w in two['game']['worms']]
    assert one['game']['opsCount']>first['game']['opsCount'],'No crater was made by the shot'
    before=two['room'].get('me') or two['room'].get('myId') or two['room'].get('myTeam')
    await other.reload(wait_until='domcontentloaded');await ready(other);await other.locator('#battle').wait_for(state='visible')
    after=await snapshot(other,code);assert len(after['room']['players'])==2
    assert before==(after['room'].get('me') or after['room'].get('myId') or after['room'].get('myTeam'))
    await other.screenshot(path=str(OUT/(engine+'-online.png')))
    record(engine,'two-independent-guests-invite-turn-security-crater-reload','pass')
   except Exception as e:
    record(engine,'two-independent-guests-online','fail',error=str(e),trace=traceback.format_exc())
    for i,c in enumerate(contexts):
     try:
      if c.pages:await c.pages[0].screenshot(path=str(OUT/(engine+'-online-failure-'+str(i)+'.png')))
     except:pass
   finally:
    if code:
     for c in contexts:
      try:
       if c.pages:await c.pages[0].evaluate("async c=>fetch('/api/rooms/'+c+'/leave',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})",code)
      except:pass
    for c in contexts:await c.close()
   await browser.close()
 if not results or any(x['status']!='pass' for x in results):raise SystemExit(1)
asyncio.run(run())
