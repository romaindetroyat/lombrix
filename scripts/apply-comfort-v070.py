"""One-time source migration, restricted to LOMBRIX. No network or credentials."""
from pathlib import Path
import subprocess

def replace_once(text, old, new, name):
    if text.count(old)!=1:
        raise RuntimeError('Unexpected source for '+name)
    return text.replace(old,new,1)

p=Path('site/app.js');s=p.read_text()
if "import {installComfortUI}" not in s:
    s="import {installComfortUI} from './comfort.js?v=0.7.0';\n"+s
    s=replace_once(s,"let options=storage.get","let comfortUI=null;\nlet options=storage.get",'UI state')
    s=replace_once(s,"function closeArsenal(){arsenalOpen=false;","function closeArsenal(){comfortUI?.close();arsenalOpen=false;",'dismiss integration')
    s=replace_once(s,"setAim();refreshCameraRail();refreshLoadout();if(arsenalOpen","setAim();refreshCameraRail();refreshLoadout();comfortUI?.refresh();if(arsenalOpen",'HUD refresh')
    s=replace_once(s,"function gestureAllowed(){return screen==='battle'&&snapshot&&!$('dialog').open;}","function gestureAllowed(){return screen==='battle'&&snapshot&&!$('dialog').open&&!comfortUI?.isOpen();}",'touch isolation')
    s=replace_once(s,"if(!canFire()||$('dialog').open||pointers.size>1||multiGesture)return;","if(!canFire()||$('dialog').open||comfortUI?.isOpen()||pointers.size>1||multiGesture)return;",'aim isolation')
    s=replace_once(s,"function arsenalDialog(){\n if(!canFire())return;","function arsenalDialog(){\n if(comfortUI){comfortUI.open('weapons');return;}\n if(!canFire())return;",'weapon selection')
    s=replace_once(s,"e.target.matches('input,select,textarea'))return;","e.target.matches('input,select,textarea')||comfortUI?.isOpen())return;",'keyboard isolation')
    s=replace_once(s,"window.addEventListener('pagehide',saveSolo);","""comfortUI=installComfortUI({$,renderer,byWeapon,storage,closeDialog,
 getState:()=>({snapshot,screen,team:myTeam(),weapon,fuse,canFire:canFire(),profile:weaponControls(byWeapon[weapon]),icon:weaponIcon}),
 beforeOpen:()=>{cancelAimGesture();stopMove();},
 setArsenalOpen:value=>{arsenalOpen=value;renderer.canAim=canFire()&&!value;},
 setFuse:value=>{fuse=value;refreshHud();}
});
window.addEventListener('pagehide',saveSolo);""",'initialization')
    p.write_text(s)
    p=Path('site/renderer.js');s=p.read_text()
    s=replace_once(s,"const reserved=occupied|| (this.h>this.w?334:(this.h<500?170:194)),focusY=(64+this.h-reserved)/2;","const reserved=this.hudInsets?.bottom??(occupied|| (this.h>this.w?334:(this.h<500?170:194))),focusY=((this.hudInsets?.top??64)+this.h-reserved)/2;",'camera framing')
    s=replace_once(s,"12/this.scale,'#fff9e8'","17*(this.uiTextScale||1)/this.scale,'#fff9e8'",'aim text')
    p.write_text(s)
    p=Path('site/index.html');p.write_text(replace_once(p.read_text(),'</head>','<link rel="stylesheet" href="/comfort.css?v=0.7.0"></head>','stylesheet'))
    for p in Path('site').glob('*'):
        if p.is_file() and p.suffix in ['.js','.html','.css','.webmanifest']:
            p.write_text(p.read_text().replace('0.6.2','0.7.0'))
    p=Path('site/sw.js');p.write_text(replace_once(p.read_text(),'const ASSETS = [',"const ASSETS = ['/comfort.js?v=0.7.0','/comfort.css?v=0.7.0',",'offline assets'))
    p=Path('scripts/build-solo.mjs');s=p.read_text()
    s=replace_once(s,"await read('site/style.css');","await read('site/style.css')+'\\n'+await read('site/comfort.css');",'solo CSS')
    s=replace_once(s,"'renderer','audio','app'","'renderer','audio','comfort','app'",'solo JS');p.write_text(s)
    p=Path('scripts/prepare-release.mjs');p.write_text(replace_once(p.read_text(),"const version='0.6.2'","const version='0.7.0'",'release version'))
subprocess.run(['node','scripts/build-solo.mjs'],check=True)
subprocess.run(['node','scripts/prepare-release.mjs'],check=True)
notes=Path('docs/v070');notes.mkdir(parents=True,exist_ok=True)
(notes/'NOTES.md').write_text('''# Interface lisible 0.7.0

Commandes de combat plus grandes. Les noms des armes passent de 9/10 pixels à 17 pixels CSS, avec un réglage 20 pixels dans le menu. Toutes les armes gardent leur nom complet dans un tiroir temporaire, à défilement vertical. Un appui équipe et ferme. La grille ne remplace pas le terrain en permanence.

Les curseurs angle/puissance sont accessibles par Visée ; la mèche reste disponible pour les armes concernées. La carte panoramique, le zoom et le recentrage sont accessibles par le bouton Caméra. Les gestes de caméra à deux doigts sont conservés. Les informations de version et de terrain sont dans le menu.

Les commandes de combat se retirent pendant le tour adverse et après la fin de la retraite. Les actions dans un tiroir ne peuvent pas déclencher un tir. Le chronomètre continue dans le tiroir d’armes ; les règles de pause et de temps de jeu ne changent pas.

Contrôle initial Chromium hors serveur : la hauteur centrale sans bande HUD passe de 151 à 230 pixels dans une fenêtre de 844 × 390 (hors zones de sécurité iOS). Ce n’est pas une mesure sur iPhone physique.

Le moteur des dégâts, le serveur autoritaire, la génération des terrains et les sessions multijoueurs sont conservés. BUILD.json recense les fichiers exacts de cette version. Les résultats de cette étape sont dans reports/v070 ; ne pas confondre vérification HTML autonome, vérification HTTPS et essais sur matériel réel.
''')
print('LOMBRIX 0.7.0 source integration complete.')
