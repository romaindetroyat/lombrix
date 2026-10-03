import subprocess,re,json,datetime,time,urllib.request,base64,os
from pathlib import Path
OUT=Path('reports');OUT.mkdir(exist_ok=True)
now=lambda:datetime.datetime.now(datetime.timezone.utc)
result={'version':'0.5.2','repository':os.environ.get('GITHUB_REPOSITORY'),'commit':os.environ.get('GITHUB_SHA'),'startedAt':now().isoformat(),'status':'pending','checks':[]}
PUBLIC_KEY='''-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArtRDfPhBjhXTXuZJuLsv
ARNtcXSKC/6W15oDlF7qL9RunaNAV9oKAAjfww2TY1K22BqgjtLpnLbJdMo4+n+P
ynEpVogS9O+0YBH0nfP8xSgAkZo/Yb7Tpr86+36P+diZg4MC7MWdNPC0uBfMuw2t
imHsFvTwXcZfrO88CAmHHtzByp1y9s1ae0Q+TMcn1eadc6md5c44w3PU5FSMpxxZ
F9u/GneTamdmjEidm0DAx4vY+ieQ2xaiiNXfNarcLUcbmHpf6/dWwuZjtxTRGHGs
XoQO3vU7reMkAbx94zF/Q4isYbKg/3a/pnMBIAaZESsyW/AIh3miNisk6LCPkWI5
c4Wg45XHML2DgD8qqKu7FM3LMo9oVbqe2IOS+aKyukGozTcaQKsjvnnP2Yh6tzfe
ERBQk8gsIrMXm1aIslwK67VviPkJg/hR2/ErwGj+D5rMwLx+hIylf8BX98nHSJQP
zRQUZNPPta9KJnaWHPFczPF0TPbHa/wkP6o8NQdXn9sefvgP0xtHxoOl5a9TWb4t
N4K+cTuGhbJTy5epSXlU3apD9mzfLmONeZ5IM9Gb4R8n94oA7W8v/hsTR6QtO31F
2d7RJORZ3ODierLp+tr0Vy+Trj6qc13qouzGaCMf04u9lqhboXX7LIY5BpFkn6VT
6rOyEvArSiV+6lTux8+Vd6sCAwEAAQ==
-----END PUBLIC KEY-----
'''
try:
 Path('/tmp/lombrix-claim-public.pem').write_text(PUBLIC_KEY)
 proc=subprocess.run(['npx','--no-install','wrangler','deploy','--temporary'],capture_output=True,text=True,timeout=240)
 text=re.sub(r'\x1b\[[0-9;]*m','',proc.stdout+'\n'+proc.stderr)
 urls=re.findall(r'https://[a-zA-Z0-9.-]+\.workers\.dev',text)
 claims=re.findall(r'https://dash\.cloudflare\.com/claim-preview\?[^\s\x1b]+',text)
 if claims:
  cipher=subprocess.run(['openssl','pkeyutl','-encrypt','-pubin','-inkey','/tmp/lombrix-claim-public.pem','-pkeyopt','rsa_padding_mode:oaep','-pkeyopt','rsa_oaep_md:sha256'],input=claims[-1].encode(),capture_output=True,check=True).stdout
  (OUT/'claim.encrypted.json').write_text(json.dumps({'cipher':'RSA-OAEP-SHA256','data':base64.b64encode(cipher).decode(),'createdAt':now().isoformat()},indent=2))
 if proc.returncode or not urls:raise RuntimeError('Wrangler deployment failed; private output withheld')
 result.update(url=urls[-1],status='deployed-unverified',claimBefore=(datetime.datetime.fromisoformat(result['startedAt'])+datetime.timedelta(minutes=60)).isoformat())
 for attempt in range(15):
  passed=True
  for path in ['/health','/','/sw.js']:
   try:
    req=urllib.request.Request(result['url']+path,headers={'User-Agent':'Mozilla/5.0','Cache-Control':'no-cache'})
    with urllib.request.urlopen(req,timeout=15) as r:
     body=r.read().decode()
     ok=r.status==200 and ((json.loads(body).get('version')=='0.5.2') if path=='/health' else ('0.5.2' in body and ('id="solo"' in body if path=='/' else 'cleanResponse' in body)))
     result['checks'].append({'path':path,'http':r.status,'verified':ok});passed=passed and ok
   except Exception as e:result['checks'].append({'path':path,'error':type(e).__name__+': '+str(e)});passed=False
  if passed:result['status']='verified-http';break
  time.sleep(4)
 (OUT/'deployment.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
 if result['status']!='verified-http':raise RuntimeError('Public HTTPS verification failed')
except Exception as e:
 result['status']='failed';result['error']=type(e).__name__+': '+str(e)
 (OUT/'deployment.json').write_text(json.dumps(result,indent=2)+'\n');print(result['error']);raise SystemExit(1)
