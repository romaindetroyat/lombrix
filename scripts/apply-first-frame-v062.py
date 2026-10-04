"""Small repeatable patch against 0.6.1; preserve the baseline rendering evidence."""
from pathlib import Path
p=Path('site/renderer.js');s=p.read_text()
old="canvas.width=Math.round(this.w*d);canvas.height=Math.round(this.h*d);this.dpr=d;"
new="const width=Math.round(this.w*d),height=Math.round(this.h*d),changed=canvas.width!==width||canvas.height!==height;this.dpr=d;if(changed){canvas.width=width;canvas.height=height;if(this.state&&this.land)this.draw(performance.now(),.001);}"
assert s.count(old)==1,'Unexpected renderer base'
p.write_text(s.replace(old,new))
p=Path('site/app.js');s=p.read_text()
old="if(which==='battle'){requestAnimationFrame(()=>renderer.resize());keepAwake();}"
new="if(which==='battle'){renderer.resize();renderer.draw(performance.now(),.001);requestAnimationFrame(()=>{renderer.resize();renderer.draw(performance.now(),.001);});keepAwake();}"
assert s.count(old)==1,'Unexpected screen entry base'
p.write_text(s.replace(old,new))
for p in Path('site').iterdir():
 if p.suffix in ['.js','.html','.css','.webmanifest']:p.write_text(p.read_text().replace('0.6.1','0.6.2'))
p=Path('scripts/prepare-release.mjs');p.write_text(p.read_text().replace("const version='0.6.1'","const version='0.6.2'"))
for oldname,newname in [('check-v061.py','check-v062.py'),('check-offline-v061.py','check-offline-v062.py'),('check-first-frame-v061.py','check-first-frame-v062.py'),('publish-v061.py','publish-v062.py')]:
 s=Path('scripts',oldname).read_text().replace('v061','v062').replace('0.6.1','0.6.2')
 if 'first-frame' in newname:s=s.replace('https://lombrix.puzzling-sousaphone-7db.workers.dev','https://127.0.0.1:8787')
 Path('scripts',newname).write_text(s)
Path('docs/v062').mkdir(parents=True,exist_ok=True)
Path('docs/v062/NOTES.md').write_text('''# LOMBRIX 0.6.2 — premières images visibles

Cette livraison conserve la barre permanente des 18 armes, les couleurs plus franches et le geste à deux doigts couvrant le décor et une commande, introduits dans 0.6.1.

Un contrôle des pixels a confirmé que le canevas WebKit restait vide dans les deux premiers prélèvements au démarrage, puis affichait le décor au prélèvement suivant. Les dimensions CSS étaient déjà correctes. Le test initial limité aux commandes ne détectait pas ce défaut. Les mesures originales restent dans `reports/v061/first-frame/result.json`.

Le canevas est désormais peint immédiatement quand le combat devient visible. Un redimensionnement identique ne réinitialise plus inutilement son bitmap ; un changement effectif de dimensions repeint le contenu sans attendre une prochaine image d'animation. Aucune modification des dégâts, de la balistique ou des règles réseau.

La validation 0.6.2 ajoute huit prélèvements de pixels (quatre par moteur) dès l'ouverture du combat, avant tout geste sur le terrain, aux contrôles d'interface, au test entre deux processus WebKit et au rechargement hors ligne. WebKit Linux n'est pas un iPhone physique. Une adresse temporaire Cloudflare n'est toujours pas un hébergement permanent.
''')
print('Applied first-frame patch; run build and measured acceptance before publication.')
