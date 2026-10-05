"""Readable HUD acceptance. WebKit/Linux is not a physical iPhone.
LOMBRIX_URL selects real HTTPS; otherwise test the identical single-file export.
"""
import asyncio,json,os,traceback
from pathlib import Path
from playwright.async_api import async_playwright
OUT=Path(os.environ.get('LOMBRIX_REPORT_DIR','reports/v070'));OUT.mkdir(parents=True,exist_ok=True)
URL=os.environ.get('LOMBRIX_URL');records=[]

def record(engine,viewport,name,status='pass',**extra):
    records.append(dict(engine=engine,viewport=viewport,name=name,status=status,**extra))
    (OUT/'interface.json').write_text(json.dumps({'version':'0.7.0','url':URL,'physicalIPhone':False,'mode':'public-https' if URL else 'self-contained-html','records':records},indent=2))
    print(engine,viewport,name,status,flush=True)

async def main():
    async with async_playwright() as pw:
        for engine in os.environ.get('LOMBRIX_ENGINES','webkit,chromium').split(','):
            browser=await getattr(pw,engine).launch(headless=True)
            for width,height in [(844,390),(667,375),(568,320),(390,844),(1440,900)]:
                size=[width,height]
                ctx=await browser.new_context(viewport={'width':width,'height':height},is_mobile=width<1000,has_touch=True,device_scale_factor=2)
                p=await ctx.new_page();p.set_default_timeout(12000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
                try:
                    if URL:
                        response=await p.goto(URL,wait_until='domcontentloaded');assert response.status==200
                    else:await p.set_content(Path('solo.html').read_text(),wait_until='domcontentloaded')
                    await p.wait_for_function("document.documentElement.dataset.lombrixReady==='true'")
                    await p.locator('#configure-solo').tap();await p.locator('#opt-worms').select_option('8');await p.locator('#opt-time').select_option('60');await p.locator('#opt-layout').select_option('ridge');await p.locator('#opt-theme').select_option('lagoon');await p.locator('#opt-seed').fill('31415');await p.locator('#confirm-config').tap()
                    await p.locator('#battle').wait_for(state='visible');await p.wait_for_timeout(700)
                    assert not errors,errors
                    for selector in ['#loadout-strip','.aim-controls','#camera-strip']:assert not await p.locator(selector).is_visible()
                    assert await p.locator('#fire').is_enabled()
                    dims=await p.evaluate('''()=>Object.fromEntries(['.battle-top','.battle-controls','#arsenal','#fire','#move-left','#move-right','#jump','#precision-toggle','#game-menu','#comfort-camera','#weapon-name'].map(sel=>{const el=document.querySelector(sel),r=el.getBoundingClientRect();return [sel,{x:r.x,y:r.y,w:r.width,h:r.height,font:getComputedStyle(el).fontSize}]}))''')
                    for selector in ['#arsenal','#fire','#move-left','#move-right','#jump','#precision-toggle','#game-menu','#comfort-camera']:
                        r=dims[selector];assert r['w']>=44 and r['h']>=44,(selector,r)
                        assert r['x']>=-1 and r['x']+r['w']<=width+1,(selector,r)
                        assert r['y']>=0 and r['y']+r['h']<=height+1,(selector,r)
                    assert float(dims['#weapon-name']['font'].replace('px',''))>=17
                    await p.screenshot(path=str(OUT/f'{engine}-game-{width}.png'))
                    record(engine,size,'readable-controls-and-clear-battlefield',centralHeight=dims['.battle-controls']['y']-dims['.battle-top']['h'],measurements=dims)
                    await p.locator('#arsenal').tap();await p.wait_for_timeout(180)
                    assert await p.locator('#loadout-strip').is_visible();assert await p.locator('[data-loadout]').count()==18
                    assert await p.locator('[data-loadout=rocket] span').inner_text()=='Patator'
                    assert await p.locator('[data-loadout=rocket] span').evaluate('e=>parseFloat(getComputedStyle(e).fontSize)')>=17
                    await p.screenshot(path=str(OUT/f'{engine}-weapons-{width}.png'))
                    await p.locator('[data-loadout=heal]').scroll_into_view_if_needed();await p.wait_for_timeout(500);await p.locator('[data-loadout=heal]').tap()
                    assert not await p.locator('#loadout-strip').is_visible();assert await p.locator('#fire-label').inner_text()=='Soigner'
                    record(engine,size,'full-labels-one-tap-equips-dismisses-without-fire')
                    await p.locator('#arsenal').tap();await p.locator('[data-loadout=grenade]').scroll_into_view_if_needed();await p.wait_for_timeout(500);await p.locator('[data-loadout=grenade]').tap()
                    await p.locator('#precision-toggle').tap();assert await p.locator('#comfort-fuse').is_visible()
                    await p.locator('[data-comfort-fuse="5"]').tap();assert await p.locator('[data-comfort-fuse="5"]').get_attribute('aria-pressed')=='true'
                    await p.locator('#power').evaluate("e=>{e.value=38;e.dispatchEvent(new Event('input',{bubbles:true}));}");await p.locator('#precision-close').tap();assert await p.locator('#power').input_value()=='38'
                    record(engine,size,'optional-precision-and-fuse-preserve-settings')
                    await p.locator('#comfort-camera').tap();assert await p.locator('#camera-strip').is_visible();await p.locator('#camera-follow').tap();assert not await p.locator('#camera-sheet').is_visible()
                    await p.locator('#arsenal').tap();await p.keyboard.press('Escape');assert not await p.locator('#loadout-strip').is_visible()
                    record(engine,size,'camera-and-escape-accessible')
                    if width==844:
                        await gesture_and_turn(p,ctx,engine,size)
                    await p.locator('#game-menu').tap();await p.locator('#menu-display').wait_for();await p.locator('#menu-display').tap();assert await p.evaluate("document.documentElement.classList.contains('large-game-text')")
                    await p.locator('#menu-resume').tap();assert await p.locator('#weapon-name').evaluate('e=>parseFloat(getComputedStyle(e).fontSize)')>=20
                    assert not errors,errors
                    record(engine,size,'20px-text-preference-and-no-page-errors')
                except Exception as exc:
                    record(engine,size,'scenario','fail',error=str(exc),trace=traceback.format_exc(),pageErrors=errors)
                    try:await p.screenshot(path=str(OUT/f'{engine}-failure-{width}.png'))
                    except Exception:pass
                finally:await ctx.close()
            await browser.close()
    if not records or any(r['status']!='pass' for r in records):raise SystemExit(1)

async def gesture_and_turn(p,ctx,engine,size):
    async def view():return json.loads(await p.locator('#game-canvas').get_attribute('data-view'))
    async def aim():return await p.evaluate("[document.querySelector('#angle').value,document.querySelector('#power').value]")
    cdp=await ctx.new_cdp_session(p) if engine=='chromium' else None
    previous={}
    async def touch(kind,pts):
        nonlocal previous
        if cdp:
            await cdp.send('Input.dispatchTouchEvent',{'type':{'start':'touchStart','move':'touchMove','end':'touchEnd'}[kind],'touchPoints':[{'id':i,'x':x,'y':y} for i,x,y in pts]})
        else:
            current={i:(x,y) for i,x,y in pts}
            changed={i:xy for i,xy in current.items() if kind=='move' or i not in previous} if kind!='end' else {i:xy for i,xy in previous.items() if i not in current}
            await p.evaluate('''({kind,pts,changed})=>{
                window.testTouchTargets||={};for(const [i,x,y] of pts)window.testTouchTargets[i]||=document.elementFromPoint(x,y);
                const make=([identifier,clientX,clientY])=>({identifier,clientX,clientY,target:window.testTouchTargets[identifier]||document.querySelector('#game-canvas')});
                const target=changed.length?make(changed[0]).target:document.querySelector('#game-canvas');
                const e=new Event('touch'+kind,{bubbles:true,cancelable:true});Object.defineProperties(e,{touches:{value:pts.map(make)},targetTouches:{value:pts.map(make)},changedTouches:{value:changed.map(make)}});target.dispatchEvent(e);
                if(kind==='end')for(const [id] of changed)delete window.testTouchTargets[id];
            }''',{'kind':kind,'pts':pts,'changed':[(i,*v) for i,v in changed.items()]})
            previous=current
        await p.wait_for_timeout(50)
    first=await view();prepared=await aim()
    await touch('start',[(1,310,145),(2,450,170)])
    for i in range(1,8):await touch('move',[(1,310-10*i,145),(2,450-10*i,170)])
    second=await view();assert second['x']>first['x']+50,(first,second);assert abs(first['zoom']-second['zoom'])<.001;assert await aim()==prepared
    await touch('end',[(1,240,145)]);await touch('move',[(1,260,180)]);assert await aim()==prepared;await touch('end',[]);await p.wait_for_timeout(650)
    record(engine,size,'two-finger-pan-keeps-aim-and-release-safe',input='native-CDP' if cdp else 'synthetic-TouchEvent',distance=second['x']-first['x'])
    first=await view();await touch('start',[(1,310,145),(2,450,170)]);await touch('move',[(1,290,130),(2,470,180)]);await touch('end',[]);await p.wait_for_timeout(650)
    assert (await view())['zoom']>first['zoom'];assert await aim()==prepared;record(engine,size,'pinch-keeps-aim')
    await p.locator('#arsenal').tap();await p.wait_for_timeout(200)
    if cdp:
        name=await p.locator('#weapon-name').inner_text();box=await p.locator('#loadout-scroll').bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']-20
        start=await p.locator('#loadout-scroll').evaluate('e=>e.scrollTop');await touch('start',[(4,x,y)])
        for i in range(1,7):await touch('move',[(4,x,y-i*18)])
        await touch('end',[]);await p.wait_for_timeout(500)
        assert await p.locator('#loadout-scroll').evaluate('e=>e.scrollTop')>start+40;assert await p.locator('#weapon-name').inner_text()==name
        record(engine,size,'native-inventory-scroll-does-not-equip')
    await p.locator('[data-loadout=rocket]').scroll_into_view_if_needed();await p.wait_for_timeout(500);await p.locator('[data-loadout=rocket]').tap()
    await p.locator('#precision-toggle').tap()
    for selector,value in [('#angle',-55),('#power',35)]:await p.locator(selector).evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}));}',value)
    await p.locator('#precision-close').tap();await p.locator('#fire').tap()
    await p.wait_for_function('document.querySelector("#round-info").textContent==="TOUR 3"',timeout=45000)
    assert await p.locator('#fire').is_visible() and await p.locator('#fire').is_enabled()
    record(engine,size,'actual-shot-AI-return-controls-restored')

asyncio.run(main())
