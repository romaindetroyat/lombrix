import asyncio,os,json,traceback,datetime
from pathlib import Path
from playwright.async_api import async_playwright
URL=os.environ['LOMBRIX_URL'];OUT=Path('reports/local');OUT.mkdir(parents=True,exist_ok=True)
result={'version':'0.5.2','url':URL,'engine':'webkit','independentBrowserProcesses':True,'physicalIPhone':False,'status':'pending','steps':[]}
def save():
 result['checkedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (OUT/'webkit-two-processes.json').write_text(json.dumps(result,indent=2)+'\n')
async def room(p,code):return await p.evaluate("async c=>(await fetch('/api/rooms/'+c+'/sync?ops=0&visible='+(document.hidden?'0':'1'))).json()",code)
async def ready(p):await p.wait_for_function("document.documentElement.dataset.lombrixReady==='true'",timeout=30000)
async def main():
 browsers=[];pages=[];code=None
 async with async_playwright() as tool:
  try:
   for _ in range(2):
    browser=await tool.webkit.launch(headless=True);browsers.append(browser)
    ctx=await browser.new_context(viewport={'width':844,'height':390},is_mobile=True,has_touch=True)
    p=await ctx.new_page();p.set_default_timeout(15000);pages.append(p)
    r=await p.goto(URL+'/',wait_until='domcontentloaded');assert r.status==200;await ready(p)
   a,b=pages
   result['visibilityAtStart']=[await p.evaluate('document.visibilityState') for p in pages];save()
   await a.locator('#nickname').fill('Alice WebKit');await a.locator('#create-duel').tap()
   await a.locator('#opt-theme').select_option('sakura');await a.locator('#opt-layout').select_option('ridge');await a.locator('#opt-seed').fill('31415');await a.locator('#opt-worms').select_option('2');await a.locator('#opt-time').select_option('60')
   await a.locator('#confirm-config').tap();await a.locator('#lobby').wait_for(state='visible');code=(await a.locator('#room-code').inner_text()).strip()
   await b.evaluate('navigator.serviceWorker.ready');await b.wait_for_function('!!navigator.serviceWorker.controller')
   await b.goto(URL+'/?room='+code,wait_until='domcontentloaded');await ready(b)
   await b.locator('#join-name').fill('Bob WebKit');await b.locator('#join-submit').tap();await b.locator('#lobby').wait_for(state='visible')
   await b.locator('#ready').tap()
   await b.wait_for_function("document.querySelector('#ready').textContent.includes('annuler')",timeout=7000)
   result['steps'].append('guest-ready-acknowledged');save()
   await a.wait_for_function('!document.querySelector("#start-room").disabled',timeout=12000)
   await a.locator('#start-room').tap()
   for p in pages:await p.locator('#battle').wait_for(state='visible')
   await a.wait_for_timeout(1000)
   active=a if await a.locator('#fire').is_enabled() else b;other=b if active==a else a
   first=await room(active,code);second=await room(other,code)
   assert first['room']['you']!=second['room']['you'];assert first['game']['key']==second['game']['key'];assert first['game']['world']==second['game']['world']
   assert [(w['id'],w['hp'],w['x'],w['y']) for w in first['game']['worms']]==[(w['id'],w['hp'],w['x'],w['y']) for w in second['game']['worms']]
   assert not await other.locator('#fire').is_enabled()
   bad=await other.evaluate("async ({c,g})=>{const r=await fetch('/api/rooms/'+c+'/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({matchId:g.key,turn:g.turn,seq:987654321,command:{type:'fire',weapon:'rocket',angle:-.5,power:.5}})});return r.status;}",{'c':code,'g':first['game']})
   assert bad in [403,409]
   for selector,value in [('#angle',-55),('#power',35)]:await active.locator(selector).evaluate('(el,v)=>{el.value=String(v);el.dispatchEvent(new Event("input",{bubbles:true}));}',value)
   await active.locator('#fire').tap()
   for p in pages:await p.wait_for_function("document.querySelector('#round-info').textContent==='TOUR 2'",timeout=35000)
   await other.wait_for_function('!document.querySelector("#fire").disabled')
   one=await room(active,code);two=await room(other,code)
   assert one['game']['opsCount']>first['game']['opsCount'];assert one['game']['ops']==two['game']['ops']
   assert [(w['id'],w['hp']) for w in one['game']['worms']]==[(w['id'],w['hp']) for w in two['game']['worms']]
   old=two['room']['you'];key=two['game']['key']
   await other.reload(wait_until='domcontentloaded');await ready(other);await other.locator('#battle').wait_for(state='visible')
   after=await room(other,code);assert after['room']['you']==old;assert after['game']['key']==key;assert len(after['room']['players'])==2
   result['steps']+=['shared-game','opponent-command-rejected','real-crater-shared','turn-transferred','reload-membership-preserved'];result['status']='pass'
   await other.screenshot(path=str(OUT/'webkit-independent-online.png'))
  except Exception as e:
   result['status']='fail';result['error']=str(e);result['trace']=traceback.format_exc();result['diagnostics']=[]
   for p in pages:
    try:
     d=await p.evaluate("({visibility:document.visibilityState,ready:document.querySelector('#ready')?.textContent,readyHidden:document.querySelector('#ready')?.hidden,startDisabled:document.querySelector('#start-room')?.disabled,hint:document.querySelector('#lobby-hint')?.textContent})")
     if code:d['packet']=await room(p,code)
     result['diagnostics'].append(d)
    except Exception as e2:result['diagnostics'].append({'error':str(e2)})
  finally:
   save();print(json.dumps(result,indent=2),flush=True)
   for p in pages:
    try:
     if code:await p.evaluate("async c=>fetch('/api/rooms/'+c+'/leave',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})",code)
    except:pass
   for browser in browsers:await browser.close()
 if result['status']!='pass':raise SystemExit(1)
asyncio.run(main())
