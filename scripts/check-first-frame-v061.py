import asyncio,json,os,base64,datetime
from pathlib import Path
from playwright.async_api import async_playwright
OUT=Path('reports/v061/first-frame');OUT.mkdir(parents=True,exist_ok=True)
URL=os.environ.get('LOMBRIX_URL','https://lombrix.puzzling-sousaphone-7db.workers.dev')
async def main():
 records=[]
 async with async_playwright() as pw:
  for engine in ['webkit','chromium']:
   b=await getattr(pw,engine).launch(headless=True)
   c=await b.new_context(viewport={'width':844,'height':390},device_scale_factor=2,is_mobile=True,has_touch=True)
   p=await c.new_page();p.set_default_timeout(25000);errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   try:
    r=await p.goto(URL+'/',wait_until='domcontentloaded');assert r.status==200
    await p.wait_for_function("document.documentElement.dataset.lombrixReady==='true'")
    await p.locator('#configure-solo').tap();await p.locator('#opt-theme').select_option('lagoon');await p.locator('#opt-layout').select_option('ridge');await p.locator('#opt-worms').select_option('8');await p.locator('#opt-time').select_option('60');await p.locator('#opt-seed').fill('31415');await p.locator('#confirm-config').tap();await p.locator('#battle').wait_for(state='visible')
    for k,delay in enumerate([0,200,600,1200]):
     await p.wait_for_timeout(delay)
     sample=await p.locator('#game-canvas').evaluate('''c=>{const ctx=c.getContext('2d'),data=ctx.getImageData(0,0,c.width,c.height).data;const colors=new Set();let opaque=0,nonzero=0;for(let i=0;i<data.length;i+=64){colors.add(data[i]+','+data[i+1]+','+data[i+2]+','+data[i+3]);if(data[i+3])opaque++;if(data[i]||data[i+1]||data[i+2])nonzero++;}return {width:c.width,height:c.height,colors:colors.size,opaque,nonzero,view:c.dataset.view,rect:c.getBoundingClientRect().toJSON(),css:{opacity:getComputedStyle(c).opacity,visibility:getComputedStyle(c).visibility,display:getComputedStyle(c).display},png:c.toDataURL('image/png')};}''')
     png=sample.pop('png');(OUT/(engine+'-canvas-'+str(k)+'.png')).write_bytes(base64.b64decode(png.split(',')[1]))
     await p.screenshot(path=str(OUT/(engine+'-screen-'+str(k)+'.png')))
     records.append({'engine':engine,'sample':k,'delayAfterPrevious':delay,'pixels':sample,'errors':errors.copy()})
   except Exception as e:records.append({'engine':engine,'error':str(e),'pageErrors':errors})
   finally:await b.close()
   (OUT/'result.json').write_text(json.dumps({'url':URL,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physicalIPhone':False,'records':records},indent=2))
 print(json.dumps(records,indent=2))
 if any('error' in x or x.get('pixels',{}).get('colors',0)<100 for x in records):raise SystemExit(1)
asyncio.run(main())
