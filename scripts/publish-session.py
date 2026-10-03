"""Requested preview publication. Never print or commit a plaintext claim URL.
Permanent CI must use the owner's authenticated Cloudflare account instead.
"""
import base64, datetime, json, os, re, subprocess, time
import urllib.error, urllib.request
from pathlib import Path

OUT=Path('reports/session'); OUT.mkdir(parents=True,exist_ok=True)
now=datetime.datetime.now(datetime.timezone.utc)
result={'repository':os.environ.get('GITHUB_REPOSITORY'),'commit':os.environ.get('GITHUB_SHA'),'version':'0.5.2','createdAt':now.isoformat(),'claimBefore':(now+datetime.timedelta(minutes=60)).isoformat(),'status':'pending','checks':[]}
try:
    assert result['repository']=='romaindetroyat/lombrix', 'Dedicated repository required'
    tests=json.loads((OUT/'two-phones/result.json').read_text())
    assert tests['results'] and all(r['status']=='pass' for r in tests['results']), 'WebKit acceptance must pass before publication'
    proc=subprocess.run(['npx','--no-install','wrangler','deploy','--temporary'],capture_output=True,text=True,timeout=240)
    text=re.sub(r'\x1b\[[0-9;]*m','',proc.stdout+'\n'+proc.stderr)
    urls=re.findall(r'https://[a-zA-Z0-9.-]+\.workers\.dev',text)
    claims=re.findall(r'https://dash\.cloudflare\.com/claim-preview\?[^\s\x1b]+',text)
    if claims:
        ciphertext=subprocess.run(['openssl','pkeyutl','-encrypt','-pubin','-inkey','scripts/claim-recipient.pem','-pkeyopt','rsa_padding_mode:oaep','-pkeyopt','rsa_oaep_md:sha256'],input=claims[-1].encode(),capture_output=True,check=True).stdout
        (OUT/'claim.encrypted.json').write_text(json.dumps({'cipher':'RSA-OAEP-SHA256','data':base64.b64encode(ciphertext).decode(),'createdAt':now.isoformat()},indent=2)+'\n')
    if proc.returncode or not urls: raise RuntimeError('Deployment failed; potentially sensitive provider output withheld')
    result.update(url=urls[-1],status='deployed-unverified')
    for attempt in range(12):
        success=True; blocked=False
        for path in ['/health','/','/sw.js']:
            try:
                request=urllib.request.Request(result['url']+path,headers={'User-Agent':'LOMBRIX-deployment-verification','Cache-Control':'no-cache'})
                with urllib.request.urlopen(request,timeout=15) as response:
                    content=response.read().decode()
                    verified=response.status==200 and (json.loads(content).get('version')=='0.5.2' if path=='/health' else ('id="solo"' in content and '0.5.2' in content if path=='/' else 'cleanResponse' in content))
                    result['checks'].append({'path':path,'http':response.status,'verified':verified})
                    success=success and verified
            except urllib.error.HTTPError as exc:
                result['checks'].append({'path':path,'http':exc.code}); success=False
                if exc.code==403: blocked=True; break
            except Exception as exc:
                result['checks'].append({'path':path,'error':type(exc).__name__});success=False
        if success: result['status']='verified-http';break
        if blocked:
            result['status']='blocked-by-host-protection';break
        time.sleep(3)
except Exception as exc:
    result['status']='failed';result['error']=str(exc)
finally:
    (OUT/'deployment.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if result['status']!='verified-http':raise SystemExit(1)
