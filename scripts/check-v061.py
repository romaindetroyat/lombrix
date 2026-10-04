"""UI regression: real pointer/touch input, never injected game results.
WebKit touch snapshots are synthetic; physical iPhone validation remains separate.
"""
import asyncio,json,os,traceback
from pathlib import Path
from playwright.async_api import async_playwright
OUT=Path(os.environ.get('LOMBRIX_REPORT_DIR','reports/v061'));OUT.mkdir(exist_ok=True,parents=True)
INLINE=os.environ.get('LOMBRIX_INLINE')=='1';URL=os.environ.get('LOMBRIX_URL','https://127.0.0.1:8787')
ENGINES=os.environ.get('LOMBRIX_ENGINES','webkit,chromium').split(',');records=[]
def report(engine,name,status,**extra):
 records.append(dict(engine=engine,name=name,status=status,**extra));print(engine,name,status,extra,flush=True)
 (OUT/'interface.json').write_text(json.dumps({'version':'0.6.1','url':None if INLINE else URL,'physicalIPhone':False,'records':records},indent=2))
async def view(p):return json.loads(await p.locator('#game-canvas').get_attribute('data-view'))
async def sliders(p):return await p.evaluate("[document.querySelector('#angle').value,document.querySelector('#power').value]")
class Touch:
 def __init__(self,p,cdp):self.p=p;self.cdp=cdp;self.prev={};self.targets={}
 async def event(self,kind,pts):
  if self.cdp:
   await self.cdp.send('Input.dispatchTouchEvent',dict(type={'start':'touchStart','move':'touchMove','end':'touchEnd','cancel':'touchCancel'}[kind],touchPoints=[dict(id=i,x=x,y=y) for i,x,y in pts]))
  else:
   current={i:(x,y) for i,x,y in pts}
   changed={i:xy for i,xy in current.items() if kind=='move' or i not in self.prev} if kind in ['start','move'] else {i:v for i,v in self.prev.items() if i not in current}
   await self.p.evaluate('''({kind,pts,changed})=>{
    window.testTouchTargets||={};for(const [i,x,y] of pts)window.testTouchTargets[i]||=document.elementFromPoint(x,y);
    const make=([identifier,clientX,clientY])=>({identifier,clientX,clientY,target:window.testTouchTargets[identifier]||document.querySelector('#game-canvas')});
    const target=changed.length?make(changed[0]).target:document.querySelector('#game-canvas');
    const e=new Event('touch'+kind,{bubbles:true,cancelable:true});Object.defineProperties(e,{touches:{value:pts.map(make)},targetTouches:{value:pts.map(make)},changedTouches:{value:changed.map(make)}});target.dispatchEvent(e);
    if(kind==='end'||kind==='cancel')for(const [id] of changed)delete window.testTouchTargets[id];
   }''',dict(kind=kind,pts=pts,changed=[(i,*v) for i,v in changed.items()]))
   self.prev=current
  await self.p.wait_for_timeout(45)
async def main():
 async with async_playwright() as tool:
  for engine in ENGINES:
   kwargs={'headless':True}
   if INLINE and engine=='chromium':kwargs.update(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
   browser=await getattr(tool,engine).launch(**kwargs)
   ctx=await browser.new_context(viewport={'width':844,'height':390},device_scale_factor=2,is_mobile=True,has_touch=True)
   p=await ctx.new_page();p.set_default_timeout(20000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   try:
    if INLINE:await p.set_content(Path('solo.html').read_text(),wait_until='domcontentloaded')
    else:
     response=await p.goto(URL+'/',wait_until='domcontentloaded');assert response.status==200
    await p.wait_for_function("document.documentElement.dataset.lombrixReady==='true'")
    await p.locator('#configure-solo').tap();await p.locator('#opt-theme').select_option('lagoon');await p.locator('#opt-layout').select_option('ridge');await p.locator('#opt-worms').select_option('8');await p.locator('#opt-time').select_option('60');await p.locator('#opt-seed').fill('31415');await p.locator('#confirm-config').tap();await p.locator('#battle').wait_for(state='visible');await p.wait_for_function('!document.querySelector("#fire").disabled');await p.wait_for_timeout(350)
    assert '0.6.1' in await p.locator('#connection').inner_text()
    assert await p.locator('#loadout-strip [data-loadout]').count()==18
    assert await p.locator('#loadout-strip').is_visible();assert await p.locator('#weapon-wheel').count()==0
    await p.screenshot(path=str(OUT/(engine+'-ribbon.png')))
    report(engine,'current-version-visible-18-weapons-permanent-no-window','pass')
    touch=Touch(p,await ctx.new_cdp_session(p) if engine=='chromium' else None)
    baseline=await view(p);shot=await sliders(p)
    # First finger on map, second on a control: capture promotion prevents stray FEU.
    f=await p.locator('#fire').bounding_box();fx=f['x']+f['width']/2;fy=f['y']+f['height']/2
    await touch.event('start',[(1,360,145)]);await touch.event('start',[(1,360,145),(2,fx,fy)])
    for i in range(1,8):await touch.event('move',[(1,360-i*10,145),(2,fx-i*10,fy)])
    after=await view(p);assert after['x']-baseline['x']>50,(baseline,after);assert abs(after['zoom']-baseline['zoom'])<.001
    assert await sliders(p)==shot;assert await p.locator('#round-info').inner_text()=='TOUR 1'
    await touch.event('end',[(1,290,145)]);await touch.event('move',[(1,310,150)]);assert await sliders(p)==shot;await touch.event('end',[])
    await p.wait_for_timeout(650);assert await p.locator('#game-canvas').get_attribute('data-gesture')=='idle';assert await p.evaluate('visualViewport.scale')==1
    report(engine,'two-finger-pan-crosses-controls-no-shot-no-aim-change','pass',moved=after['x']-baseline['x'])
    before=await view(p)
    await touch.event('start',[(1,320,130),(2,460,180)]);await touch.event('move',[(1,300,110),(2,480,170)]);await touch.event('end',[])
    await p.wait_for_timeout(650);after=await view(p);assert after['zoom']>before['zoom'];assert await sliders(p)==shot
    report(engine,'map-two-finger-pinch-anchored-and-camera-safe','pass')
    await p.locator('#loadout-scroll [data-loadout=grenade]').tap();assert 'Grenade' in await p.locator('#weapon-name').inner_text();assert await p.locator('#round-info').inner_text()=='TOUR 1'
    assert not await p.locator('#dialog').evaluate('e=>e.open')
    t=await p.locator('#timer').inner_text();await p.wait_for_timeout(1200);assert await p.locator('#timer').inner_text()!=t
    report(engine,'one-tap-equips-without-modal-pause-or-fire','pass')
    if engine=='chromium':
     box=await p.locator('#loadout-scroll').bounding_box();cy=box['y']+box['height']/2;x=box['x']+box['width']-90
     start=await p.locator('#loadout-scroll').evaluate('e=>e.scrollLeft');chosen=await p.locator('#weapon-name').inner_text()
     await touch.event('start',[(4,x,cy)])
     for i in range(1,10):await touch.event('move',[(4,x-i*30,cy)])
     await touch.event('end',[]);await p.wait_for_timeout(500)
     assert await p.locator('#loadout-scroll').evaluate('e=>e.scrollLeft')>start+80;assert await p.locator('#weapon-name').inner_text()==chosen
     report(engine,'native-ribbon-swipe-scrolls-without-equipping','pass')
    await p.locator('[data-loadout=heal]').scroll_into_view_if_needed();await p.wait_for_timeout(500);await p.locator('[data-loadout=heal]').tap();assert await p.locator('#fire-label').inner_text()=='SOIGNER'
    await p.locator('[data-loadout=rocket]').scroll_into_view_if_needed();await p.locator('[data-loadout=rocket]').focus();await p.keyboard.press('Enter');assert await p.locator('#round-info').inner_text()=='TOUR 1';assert await p.locator('#weapon-name').inner_text()=='Patator'
    report(engine,'utilities-and-keyboard-selection-never-fire','pass')
    await p.locator('#angle').evaluate("e=>{e.value=-55;e.dispatchEvent(new Event('input',{bubbles:true}));}");await p.locator('#power').evaluate("e=>{e.value=35;e.dispatchEvent(new Event('input',{bubbles:true}));}");await p.locator('#fire').tap();await p.wait_for_function('document.querySelector("#round-info").textContent==="TOUR 3"',timeout=45000)
    report(engine,'real-shot-AI-riposte-player-return','pass')
    await touch.event('start',[(1,300,125),(2,440,160)]);await p.set_viewport_size({'width':390,'height':844});await touch.event('cancel',[]);await p.wait_for_timeout(700)
    assert await p.locator('#game-canvas').get_attribute('data-gesture')=='idle';assert await p.locator('#loadout-strip').is_visible()
    await p.locator('[data-loadout=banana]').scroll_into_view_if_needed();await p.locator('[data-loadout=banana]').tap();assert 'Banane' in await p.locator('#weapon-name').inner_text()
    await p.screenshot(path=str(OUT/(engine+'-portrait.png')));assert not errors,errors
    report(engine,'portrait-rotation-cancellation-and-equipment-accessible','pass')
   except Exception as e:
    report(engine,'UI-scenario','fail',error=str(e),trace=traceback.format_exc(),pageErrors=errors)
    try:await p.screenshot(path=str(OUT/(engine+'-failure.png')))
    except:pass
   finally:await ctx.close();await browser.close()
 if not records or any(r['status']!='pass' for r in records):raise SystemExit(1)
asyncio.run(main())
