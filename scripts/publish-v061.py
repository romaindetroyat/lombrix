"""Publish only the validated 0.6.1 game. Never print credentials or a claim URL."""
import base64, datetime, hashlib, json, os, re, subprocess, time
import urllib.error, urllib.request
from pathlib import Path
OUT=Path('reports/v061/session');OUT.mkdir(parents=True,exist_ok=True)
now=datetime.datetime.now(datetime.timezone.utc)
result={'repository':os.environ.get('GITHUB_REPOSITORY'),'commit':os.environ.get('GITHUB_SHA'),'version':'0.6.1','createdAt':now.isoformat(),'status':'pending','checks':[]}
KEY='''-----BEGIN PUBLIC KEY-----
MIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEAteXQ3OvgfMP+D1AZvVoS
RXaUbyDy4mKlm9Xt5fb1ujJIb8OWRponVI48H1CUVRzaXt1Duud9MLsXC3KCCiFj
gAMmiwGl+u+qYLPcfc3cyFzJmJgLp0SrXHPi1HX3hV/b/MEtjUkEuEx1d8WlcfhQ
12eo9+uUriZZBranWjZqjgCzdbKbC3gpVYX/+JhTTvJhfb8l9TvuQnemU2GHw6I9
q1STLPoLQ3KhK1VUyJHs/hofcLgpt+cFrQM13Sk3SQ6A/cT+LL++nePU+5etDP7x
Qe7kAWfl8TUKLiYdsfvXTNPsobV4OepZkGVv3deMvwGWGz/qF+oxKjFybMfx3UZ8
X3bxPCKpzUgU+3O1dSjis5X3DeFGqgGWM7oCBX1+o2PtAdBH00SPApxxOkyujkrX
uqbWQdeHEY2I2L0aj6N0a/EFeOFdbC+H8zl+UcQmoonZKvoAg1gQKKLoYMpJQNdH
rt7FAXDyyP+TlTJV+Bz4GU7Ol58wcijXJovfs4PWdSRnAgMBAAE=
-----END PUBLIC KEY-----
'''
try:
    assert result['repository']=='romaindetroyat/lombrix','Dedicated repository required'
    gate=json.loads(Path('reports/v061/gate.json').read_text())
    assert gate.get('allPassed') is True and gate.get('version')=='0.6.1','Every acceptance gate must pass'
    build=json.loads(Path('BUILD.json').read_text())
    assert build['version']=='0.6.1'
    for path,digest in build['files'].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,'Build differs: '+path
    permanent=bool(os.environ.get('CLOUDFLARE_API_TOKEN'))
    result['hosting']='authenticated-account' if permanent else 'temporary-unclaimed'
    args=['npx','--no-install','wrangler','deploy']+([] if permanent else ['--temporary'])
    proc=subprocess.run(args,capture_output=True,text=True,timeout=240)
    text=re.sub(r'\x1b\[[0-9;]*m','',proc.stdout+'\n'+proc.stderr)
    urls=re.findall(r'https://[a-zA-Z0-9.-]+\.workers\.dev',text)
    claims=re.findall(r'https://dash\.cloudflare\.com/claim-preview\?[^\s\x1b]+',text)
    if claims:
        Path('/tmp/lombrix-v061-public.pem').write_text(KEY)
        cipher=subprocess.run(['openssl','pkeyutl','-encrypt','-pubin','-inkey','/tmp/lombrix-v061-public.pem','-pkeyopt','rsa_padding_mode:oaep','-pkeyopt','rsa_oaep_md:sha256'],input=claims[-1].encode(),capture_output=True,check=True).stdout
        (OUT/'claim.encrypted.json').write_text(json.dumps({'cipher':'RSA-OAEP-SHA256','data':base64.b64encode(cipher).decode()},indent=2)+'\n')
        result['claimBefore']=(now+datetime.timedelta(minutes=60)).isoformat()
    if proc.returncode or not urls:raise RuntimeError('Deployment rejected by provider; sensitive output withheld')
    result.update(url=urls[-1],status='deployed-unverified')
    for attempt in range(12):
        success=True;blocked=False
        for path in ['/health','/','/sw.js']:
            try:
                req=urllib.request.Request(result['url']+path,headers={'User-Agent':'LOMBRIX-release-check','Cache-Control':'no-cache'})
                with urllib.request.urlopen(req,timeout=15) as response:
                    content=response.read().decode()
                    valid=response.status==200 and (json.loads(content).get('version')=='0.6.1' if path=='/health' else ('0.6.1' in content and ('id="solo"' in content if path=='/' else 'cleanResponse' in content)))
                    result['checks'].append({'path':path,'http':response.status,'verified':valid});success=success and valid
            except urllib.error.HTTPError as e:
                result['checks'].append({'path':path,'http':e.code});success=False
                if e.code==403:blocked=True;break
            except Exception as e:result['checks'].append({'path':path,'error':type(e).__name__});success=False
        if success:result['status']='verified-http';break
        if blocked:result['status']='blocked-by-host-protection';break
        time.sleep(3)
except Exception as e:
    result['status']='failed';result['error']=str(e)
finally:
    (OUT/'deployment.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if result['status']!='verified-http':raise SystemExit(1)
