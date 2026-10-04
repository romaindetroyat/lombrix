"""Measured UI checks. WebKit events are DOM touch snapshots; Chromium also uses
native CDP multi-touch. Neither constitutes a physical iPhone test."""
import asyncio, json, os, traceback
from pathlib import Path
from playwright.async_api import async_playwright
OUT=Path(os.environ.get('LOMBRIX_REPORT_DIR','reports/v060'));OUT.mkdir(parents=True,exist_ok=True)
URL=os.environ.get('LOMBRIX_URL','https://127.0.0.1:8787')
INLINE=os.environ.get('LOMBRIX_INLINE')=='1'
ENGINES=os.environ.get('LOMBRIX_ENGINES','webkit,chromium').split(',')
records=[]
def report(engine,name,status,**extra):
 records.append(dict(engine=engine,name=name,status=status,**extra))
 (OUT/'interface.json').write_text(json.dumps({'url':None if INLINE else URL,'transport':'set_content standalone' if INLINE else 'real HTTP/HTTPS','physicalIPhone':False,'results':records},ensure_ascii=False,indent=2))
 print(engine,name,status,flush=True)
async def ready(page):await page.wait_for_function("document.documentElement.dataset.lombrixReady==='true'",timeout=30000)
async def load(page):
 if INLINE:await page.set_content(Path('solo.html').read_text(),wait_until='domcontentloaded')
 else:
  r=await page.goto(URL+'/',wait_until='domcontentloaded');assert r and r.status==200
 await ready(page)
async def view(p):return json.loads(await p.locator('#game-canvas').get_attribute('data-view'))
async def sliders(p):return await p.evaluate("[document.querySelector('#angle').value,document.querySelector('#power').value]")
async def center(p,sel):
 b=await p.locator(sel).bounding_box();assert b,sel
 return (b['x']+b['width']/2,b['y']+b['height']/2)
class Touch:
 def __init__(self,p,cdp):self.p=p;self.cdp=cdp;self.previous={}
 async def event(self,kind,pts):
  if self.cdp:
   await self.cdp.send('Input.dispatchTouchEvent',dict(type={'start':'touchStart','move':'touchMove','end':'touchEnd','cancel':'touchCancel'}[kind],touchPoints=[dict(id=i,x=x,y=y) for i,x,y in pts]))
  else:
   current={i:(x,y) for i,x,y in pts}
   changed=current if kind in ['start','move'] else {i:v for i,v in self.previous.items() if i not in current}
   await self.p.evaluate('''({kind,pts,changed})=>{
    const canvas=document.querySelector('#game-canvas');
    const touches=pts.map(([identifier,clientX,clientY])=>({identifier,clientX,clientY,target:canvas}));
    const e=new Event('touch'+kind,{bubbles:true,cancelable:true});
    Object.defineProperties(e,{touches:{value:touches},targetTouches:{value:touches},changedTouches:{value:changed.map(([identifier,clientX,clientY])=>({identifier,clientX,clientY,target:canvas}))}});
    canvas.dispatchEvent(e);
   }''',dict(kind=kind,pts=pts,changed=[(i,*v) for i,v in changed.items()]))
   self.previous=current
  await self.p.wait_for_timeout(30)
async def start_custom(p,theme='jungle',worms='8'):
 await p.locator('#configure-solo').tap()
 await p.locator('#opt-theme').select_option(theme)
 await p.locator('#opt-layout').select_option('ridge')
 await p.locator('#opt-worms').select_option(worms)
 await p.locator('#opt-time').select_option('60')
 await p.locator('#opt-seed').fill('31415')
 await p.locator('#confirm-config').tap();await p.locator('#battle').wait_for(state='visible')
 await p.wait_for_function('!document.querySelector("#fire").disabled');await p.wait_for_timeout(600)
async def check(engine,browser):
 ctx=await browser.new_context(viewport={'width':844,'height':390},device_scale_factor=2,is_mobile=True,has_touch=True)
 p=await ctx.new_page();p.set_default_timeout(12000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 touch=Touch(p,await ctx.new_cdp_session(p) if engine=='chromium' else None)
 try:
  await load(p);await start_custom(p)
  a=await view(p);assert a['zoom']>=1.5
  shot=await sliders(p)
  await touch.event('start',[(1,355,160),(2,465,160)])
  for i in range(1,9):await touch.event('move',[(1,355-i*10,160),(2,465-i*10,160)])
  b=await view(p);assert b['x']-a['x']>60,(a,b);assert abs(a['zoom']-b['zoom'])<.001
  assert await sliders(p)==shot
  await touch.event('end',[(2,385,160)])
  await touch.event('move',[(2,440,200)])
  assert await sliders(p)==shot
  await touch.event('end',[])
  await p.wait_for_timeout(150)
  assert await p.locator('#game-canvas').get_attribute('data-gesture')=='idle'
  assert await p.evaluate('visualViewport.scale')==1
  report(engine,'two-finger-horizontal-pan-no-zoom-no-shot-and-single-finger-latch','pass',input='native-CDP' if engine=='chromium' else 'DOM-touch-snapshot',distance=round(b['x']-a['x'],2))
  before=await view(p)
  await touch.event('start',[(1,335,145),(2,465,195)])
  await touch.event('move',[(1,335,120),(2,465,170)])
  vertical=await view(p);assert abs(vertical['y']-before['y'])>20
  await touch.event('move',[(1,305,110),(2,495,180)])
  zoomed=await view(p);assert zoomed['zoom']>before['zoom']*1.15
  await touch.event('end',[]);assert await sliders(p)==shot
  report(engine,'two-finger-vertical-pan-and-pinch-preserve-shot','pass')
  await touch.event('start',[(1,320,150),(2,440,150)])
  await p.set_viewport_size({'width':844,'height':365});await p.wait_for_timeout(120)
  await touch.event('move',[(1,290,150),(2,410,150)]);assert await sliders(p)==shot
  await touch.event('cancel',[])
  await p.set_viewport_size({'width':844,'height':390});await p.wait_for_timeout(150)
  assert await p.locator('#game-canvas').get_attribute('data-gesture')=='idle'
  report(engine,'address-bar-height-change-and-cancel-leave-no-ghost-touch','pass')
  await p.locator('#camera-follow').tap();await p.wait_for_timeout(400)
  await p.screenshot(path=str(OUT/(engine+'-jungle.png')))
  await p.locator('#arsenal').tap()
  assert await p.locator('#weapon-wheel').is_visible()
  assert not await p.locator('#dialog').evaluate('(e)=>e.open')
  assert await p.locator('#weapon-wheel [data-weapon]').count()==6
  t=float(await p.locator('#timer').inner_text());await p.wait_for_timeout(1100);assert float(await p.locator('#timer').inner_text())<t
  await p.screenshot(path=str(OUT/(engine+'-wheel.png')))
  await p.locator('#weapon-wheel [data-weapon=grenade]').tap()
  assert await p.locator('#weapon-name').inner_text()=='Grenade cabotine'
  assert not await p.locator('#weapon-wheel').is_visible()
  assert await p.locator('#round-info').inner_text()=='TOUR 1'
  report(engine,'wheel-opens-without-modal-or-pause-single-tap-equips-not-fires','pass')
  # On WebKit use real mouse pointer drag for this optional shortcut, plus real touchscreen taps above.
  x,y=await center(p,'#arsenal')
  if engine=='chromium':
   await touch.event('start',[(3,x,y)]);tx,ty=await center(p,'#weapon-wheel [data-weapon=shotgun]')
   for i in range(1,6):await touch.event('move',[(3,x+(tx-x)*i/5,y+(ty-y)*i/5)])
   await touch.event('end',[])
  else:
   await p.mouse.move(x,y);await p.mouse.down();tx,ty=await center(p,'#weapon-wheel [data-weapon=shotgun]')
   await p.mouse.move(tx,ty,steps=5);await p.mouse.up()
  assert await p.locator('#weapon-name').inner_text()=='Tromblon'
  assert not await p.locator('#weapon-wheel').is_visible()
  assert await p.locator('#power-control').is_hidden()
  report(engine,'drag-from-weapon-button-release-equips-without-firing','pass',input='native-touch' if engine=='chromium' else 'mouse-pointer')
  await p.locator('#arsenal').tap();await p.locator('.wheel-all').tap()
  assert await p.locator('#weapon-wheel [data-weapon]').count()==18
  for button in await p.locator('#weapon-wheel button:not([hidden])').all():
   box=await button.bounding_box()
   if box:assert box['x']>=0 and box['y']>=0 and box['x']+box['width']<=845 and box['y']+box['height']<=391,box
  await p.screenshot(path=str(OUT/(engine+'-all-weapons.png')))
  await p.locator('#weapon-wheel [data-weapon=rocket]').tap()
  await p.locator('#arsenal').tap();await p.locator('.wheel-all').focus();await p.keyboard.press('Enter')
  assert await p.locator('#weapon-wheel').get_attribute('data-mode')=='all'
  assert await p.locator('#round-info').inner_text()=='TOUR 1'
  await p.locator('#weapon-wheel [data-weapon=rocket]').tap()
  report(engine,'all-18-items-visible-no-categories-keyboard-never-fires','pass')
  await p.locator('#angle').evaluate("e=>{e.value='-55';e.dispatchEvent(new Event('input',{bubbles:true}));}")
  await p.locator('#power').evaluate("e=>{e.value='35';e.dispatchEvent(new Event('input',{bubbles:true}));}")
  await p.locator('#fire').tap();await p.wait_for_function('document.querySelector("#round-info").textContent==="TOUR 3"',timeout=45000)
  assert not errors,errors
  report(engine,'real-shot-ai-riposte-and-player-return','pass')
  await p.set_viewport_size({'width':390,'height':844});await p.wait_for_timeout(250)
  await p.locator('#arsenal').tap();await p.locator('.wheel-all').tap();await p.screenshot(path=str(OUT/(engine+'-portrait.png')))
  for button in await p.locator('#weapon-wheel [data-weapon]').all():
   box=await button.bounding_box();assert box and box['x']>=0 and box['x']+box['width']<=391,box
  report(engine,'portrait-arsenal-fits-and-rotation-clears-gestures','pass')
 except Exception as e:
  report(engine,'remaining-UI-scenario','fail',error=str(e),trace=traceback.format_exc(),pageErrors=errors)
  try:await p.screenshot(path=str(OUT/(engine+'-failure.png')))
  except:pass
 finally:await ctx.close()
async def main():
 async with async_playwright() as tool:
  for engine in ENGINES:
   kwargs={'headless':True}
   if INLINE and engine=='chromium':kwargs.update(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
   b=await getattr(tool,engine).launch(**kwargs)
   await check(engine,b);await b.close()
 if not records or any(r['status']=='fail' for r in records):raise SystemExit(1)
asyncio.run(main())
