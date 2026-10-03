"""Two independent browser processes emulate two foreground phones.
No game state, visibility override, or ready action is injected. Actions use UI.
The existing one-browser-context failures are retained in reports/local/.
"""
import asyncio, datetime, json, os, traceback
from pathlib import Path
from playwright.async_api import async_playwright

URL = os.environ.get('LOMBRIX_URL', 'http://127.0.0.1:8787').rstrip('/')
OUT = Path(os.environ.get('LOMBRIX_REPORT_DIR', 'reports/two-phones'))
OUT.mkdir(parents=True, exist_ok=True)
report = {'url': URL, 'commit': os.environ.get('GITHUB_SHA'), 'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'deviceModel': 'two independent WebKit processes; not physical iPhones', 'results': []}

def save():
    (OUT / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

async def loaded(page, path='/'):
    response = await page.goto(URL + path, wait_until='domcontentloaded', timeout=30000)
    assert response and response.status == 200, 'Navigation must return HTTP 200'
    await page.wait_for_function("document.documentElement.dataset.lombrixReady === 'true'", timeout=25000)

async def read_room(page, code, sync=False):
    suffix = '/sync?ops=0' if sync else ''
    return await page.evaluate("async ({c,s}) => { const r=await fetch('/api/rooms/'+c+s); return {http:r.status,data:await r.json()}; }", {'c': code, 's': suffix})

async def main():
    peers = []; contexts = []; pages = []; code = None; requests = []; errors = []
    try:
        async with async_playwright() as pw:
            try:
                for index in range(2):
                    browser = await pw.webkit.launch(headless=True)
                    peers.append(browser)
                    ctx = await browser.new_context(viewport={'width':844, 'height':390}, device_scale_factor=2, is_mobile=True, has_touch=True)
                    contexts.append(ctx)
                    page = await ctx.new_page(); page.set_default_timeout(20000); pages.append(page)
                    page.on('pageerror', lambda e, i=index: errors.append({'phone':i,'error':str(e)}))
                    page.on('response', lambda r, i=index: requests.append({'phone':i,'path':r.url.split(URL)[-1].split('?')[0], 'http':r.status}) if '/api/' in r.url else None)
                    await loaded(page)
                a,b=pages
                await a.locator('#nickname').fill('Alice validation')
                await a.locator('#create-duel').tap()
                await a.locator('#opt-theme').select_option('sakura')
                await a.locator('#opt-layout').select_option('ridge')
                await a.locator('#opt-seed').fill('31415')
                await a.locator('#opt-worms').select_option('2')
                await a.locator('#opt-time').select_option('60')
                await a.locator('#confirm-config').tap()
                await a.locator('#lobby').wait_for(state='visible')
                code=(await a.locator('#room-code').inner_text()).strip()
                await b.evaluate('navigator.serviceWorker.ready')
                await b.wait_for_function('!!navigator.serviceWorker.controller')
                await loaded(b,'/?room='+code)
                await b.locator('#join-name').fill('Bob validation')
                await b.locator('#join-submit').tap()
                await b.locator('#lobby').wait_for(state='visible')
                await b.locator('#ready').tap()
                await b.wait_for_function('document.querySelector("#ready").textContent.includes("annuler")')
                await a.wait_for_function('!document.querySelector("#start-room").disabled')
                report['lobby']=[{'phone':i,'visibility':await p.evaluate('document.visibilityState'),'state':await read_room(p,code)} for i,p in enumerate(pages)]
                await a.locator('#start-room').tap()
                for p in pages: await p.locator('#battle').wait_for(state='visible')
                await a.wait_for_timeout(1200)
                initial=[(await read_room(p,code,True))['data'] for p in pages]
                assert initial[0]['room']['you'] != initial[1]['room']['you']
                assert initial[0]['game']['key'] == initial[1]['game']['key']
                assert initial[0]['game']['world'] == initial[1]['game']['world']
                active=a if await a.locator('#fire').is_enabled() else b
                other=b if active==a else a
                assert await active.locator('#fire').is_enabled()
                assert not await other.locator('#fire').is_enabled()
                first=(await read_room(active,code,True))['data']
                status=await other.evaluate("""async ({c,g}) => { const r=await fetch('/api/rooms/'+c+'/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({matchId:g.key,turn:g.turn,seq:987654321,command:{type:'fire',weapon:'rocket',angle:-0.5,power:0.5}})}); return r.status; }""", {'c':code,'g':first['game']})
                assert status in (403,409),'Opponent command was not rejected'
                for selector,value in [('#angle',-55),('#power',35)]:
                    await active.locator(selector).evaluate('(el,v)=>{el.value=String(v);el.dispatchEvent(new Event("input",{bubbles:true}));}',value)
                await active.locator('#fire').tap()
                for p in pages:
                    await p.wait_for_function('document.querySelector("#round-info").textContent === "TOUR 2"', timeout=35000)
                await other.wait_for_function('!document.querySelector("#fire").disabled')
                settled=[(await read_room(p,code,True))['data'] for p in pages]
                assert settled[0]['game']['ops'] == settled[1]['game']['ops']
                assert settled[0]['game']['opsCount'] > first['game']['opsCount']
                for x,y in zip(sorted(settled[0]['game']['worms'],key=lambda w:w['id']), sorted(settled[1]['game']['worms'],key=lambda w:w['id'])):
                    for key in ['id','team','hp','maxHp','name']: assert x[key]==y[key], key
                    for key in ['x','y']: assert abs(x[key]-y[key])<0.15, key
                before=(await read_room(other,code,True))['data']
                await other.reload(wait_until='domcontentloaded')
                await other.wait_for_function("document.documentElement.dataset.lombrixReady==='true'")
                await other.locator('#battle').wait_for(state='visible')
                after=(await read_room(other,code,True))['data']
                assert after['room']['you']==before['room']['you']
                assert len(after['room']['players'])==2
                assert after['game']['key']==before['game']['key']
                assert not errors, errors
                await other.screenshot(path=str(OUT/'webkit-two-phones.png'))
                report['results'].append({'step':'invitation-readiness-shot-authority-shared-crater-turn-reload','status':'pass'})
            except Exception as exc:
                report['results'].append({'step':'two-phones','status':'fail','error':str(exc),'trace':traceback.format_exc()})
                report['diagnostics']=[]
                for i,p in enumerate(pages):
                    try:
                        report['diagnostics'].append({'phone':i, 'visibility':await p.evaluate('document.visibilityState'),'room':await read_room(p,code) if code else None,'screen':await p.locator('body').inner_text()})
                        await p.screenshot(path=str(OUT/f'failure-{i}.png'))
                    except Exception as nested: report['diagnostics'].append({'phone':i,'error':str(nested)})
            finally:
                report['pageErrors']=errors; report['lastRequests']=requests[-30:]; save()
                for p in pages:
                    if code:
                        try: await p.evaluate("async c=>fetch('/api/rooms/'+c+'/leave',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})",code)
                        except Exception: pass
                for browser in peers: await browser.close()
    finally: save()
    print(json.dumps(report['results'],indent=2))
    if not report['results'] or any(r['status']!='pass' for r in report['results']): raise SystemExit(1)

asyncio.run(main())
