/** Progressive disclosure for the combat HUD. No gameplay or networking rules. */
export function installComfortUI({$,renderer,byWeapon,storage,getState,beforeOpen,setArsenalOpen,setFuse,closeDialog}) {
  const battle=$('battle'), controls=battle.querySelector('.battle-controls');
  const ribbon=$('loadout-strip'), scroll=$('loadout-scroll');
  let panel=null,opener=null,lastWeapon=null,quiet=false;
  battle.classList.add('comfort-hud');
  const make=(tag,id,html,cls='')=>{const el=document.createElement(tag);el.id=id;el.className=cls;el.innerHTML=html;return el;};
  const dismiss=make('button','hud-dismiss','');dismiss.type='button';dismiss.hidden=true;dismiss.setAttribute('aria-label','Fermer le panneau et revenir au terrain');battle.append(dismiss);
  const header=(title,closeId)=>`<header class="hud-sheet-head"><h2>${title}</h2><button type="button" id="${closeId}" class="sheet-close" aria-label="Fermer">×</button></header>`;
  ribbon.classList.add('hud-sheet');ribbon.hidden=true;ribbon.setAttribute('role','dialog');ribbon.setAttribute('aria-modal','true');ribbon.setAttribute('aria-label','Choisir une arme');
  ribbon.prepend(make('div','equipment-head',header('Choisir une arme','equipment-close')+'<p class="sheet-note">18 équipements · Un appui pour équiper.</p>'));
  ribbon.querySelector('.loadout-hint')?.remove();
  for(const button of scroll.querySelectorAll('[data-loadout]'))button.querySelector('span').textContent=byWeapon[button.dataset.loadout].name;
  const aimControls=controls.querySelector('.aim-controls');
  const precision=make('section','precision-sheet',header('Régler le tir','precision-close'),'hud-sheet');precision.hidden=true;
  precision.setAttribute('role','dialog');precision.setAttribute('aria-modal','true');precision.setAttribute('aria-label','Réglage précis du tir');precision.append(aimControls);
  const fuseBox=make('div','comfort-fuse','<span>Durée de la mèche</span><div>'+[1,3,5].map(n=>`<button type="button" data-comfort-fuse="${n}" aria-pressed="false">${n} s</button>`).join('')+'</div>');precision.append(fuseBox);battle.append(precision);
  const precisionButton=make('button','precision-toggle','<span>Visée</span><strong id="shot-readout">50 %</strong>','precision-toggle');precisionButton.type='button';precisionButton.setAttribute('aria-controls','precision-sheet');precisionButton.setAttribute('aria-expanded','false');$('fire').before(precisionButton);
  const camera=make('section','camera-sheet',header('Explorer le terrain','camera-close')+'<p class="sheet-note">Glisse deux doigts pour déplacer la vue. Pince pour zoomer.</p>','hud-sheet');camera.hidden=true;camera.setAttribute('role','dialog');camera.setAttribute('aria-modal','true');camera.setAttribute('aria-label','Caméra et carte');
  camera.append($('camera-strip'));camera.append(battle.querySelector('.view-controls'));battle.append(camera);
  const cameraButton=make('button','comfort-camera','◎','icon-btn');cameraButton.type='button';cameraButton.setAttribute('aria-label','Caméra : carte, zoom et recentrage');cameraButton.setAttribute('aria-controls','camera-sheet');cameraButton.setAttribute('aria-expanded','false');$('game-menu').before(cameraButton);
  const wind=$('wind');wind.classList.add('comfort-wind');battle.querySelector('.turn-clock').append(wind);
  const weaponButton=$('arsenal');weaponButton.setAttribute('aria-controls','loadout-strip');weaponButton.setAttribute('aria-expanded','false');
  // The nested fuse link was difficult to hit and competed with the weapon button.
  $('fuse-hint').tabIndex=-1;$('fuse-hint').removeAttribute('role');
  $('fire-icon').hidden=true;
  const closeBtn={weapons:$('equipment-close'),precision:$('precision-close'),camera:$('camera-close')};
  const sheets={weapons:ribbon,precision,camera};
  const triggers={weapons:weaponButton,precision:precisionButton,camera:cameraButton};
  function close({restoreFocus=true}={}) {
    const was=panel;panel=null;for(const el of Object.values(sheets))el.hidden=true;
    for(const el of Object.values(triggers))el.setAttribute('aria-expanded','false');
    dismiss.hidden=true;battle.classList.remove('hud-sheet-open');setArsenalOpen(false);
    if(was&&restoreFocus&&opener&&!opener.disabled&&opener.getClientRects().length)opener.focus({preventScroll:true});opener=null;
  }
  function open(kind) {
    const s=getState();if(s.screen!=='battle'||(!s.canFire&&kind!=='camera'))return;
    if(panel===kind){close();return;}close({restoreFocus:false});beforeOpen();
    panel=kind;opener=triggers[kind];sheets[kind].hidden=false;dismiss.hidden=false;battle.classList.add('hud-sheet-open');setArsenalOpen(kind==='weapons');
    triggers[kind].setAttribute('aria-expanded','true');renderer.canAim=false;
    if(kind==='weapons'){
      const selected=scroll.querySelector(`[data-loadout="${s.weapon}"]`);
      requestAnimationFrame(()=>{if(panel!=='weapons')return;scroll.scrollTop=Math.max(0,(selected?.offsetTop||0)-scroll.offsetTop-8);(selected||closeBtn.weapons).focus({preventScroll:true});});
    }else closeBtn[kind].focus({preventScroll:true});
  }
  dismiss.onclick=()=>close();for(const kind of Object.keys(sheets))closeBtn[kind].onclick=()=>close();
  precisionButton.onclick=()=>open('precision');cameraButton.onclick=()=>open('camera');
  $('camera-follow').textContent='Recentrer';
  $('camera-follow').addEventListener('click',()=>close());
  for(const b of fuseBox.querySelectorAll('button'))b.onclick=()=>setFuse(Number(b.dataset.comfortFuse));
  // Escape and focus containment are independent of the running turn timer.
  document.addEventListener('keydown',e=>{
    if(!panel)return;
    if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();close();return;}
    if(e.key==='Tab'){
      const list=[...sheets[panel].querySelectorAll('button:not(:disabled),input:not(:disabled),[tabindex="0"]')].filter(el=>el.getClientRects().length);
      const i=list.indexOf(document.activeElement);if(e.shiftKey&&(i<=0)){e.preventDefault();list.at(-1)?.focus();}else if(!e.shiftKey&&(i===list.length-1||i<0)){e.preventDefault();list[0]?.focus();}
    }
    // A focused range or drawer button must not also move the worm or fire.
    if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown',' ','Enter'].includes(e.key)&&!sheets[panel].contains(e.target)){e.preventDefault();e.stopImmediatePropagation();}
  },true);
  // Respect a user's larger UI preference; never shrink labels to fit more items.
  let large=storage.get('lombrix-large-text',false)===true;
  function applyText(){document.documentElement.classList.toggle('large-game-text',large);renderer.uiTextScale=large?1.15:1;}
  applyText();
  const dialogBody=$('dialog-body');
  const observer=new MutationObserver(()=>{
    if(!$('menu-resume')||$('menu-display'))return;
    const b=make('button','menu-display',large?'Lisibilité : très grands textes':'Lisibilité : grands textes');
    b.type='button';$('menu-help').before(b);
    b.onclick=()=>{large=!large;storage.set('lombrix-large-text',large);applyText();b.textContent=large?'Lisibilité : très grands textes':'Lisibilité : grands textes';};
    const map=make('button','menu-camera','Carte, zoom et caméra');map.type='button';b.before(map);map.onclick=()=>{closeDialog();open('camera');};
    const detail=make('p','menu-build','');detail.className='sheet-note';dialogBody.append(detail);const s=getState();detail.textContent=$('connection').textContent+' · '+$('round-info').textContent+' · '+($('battle-level').textContent||'');
  });observer.observe(dialogBody,{childList:true});
  function refresh() {
    const s=getState();if(!s.snapshot)return;
    const def=byWeapon[s.weapon],profile=s.profile;
    precisionButton.disabled=!s.canFire;
    weaponButton.disabled=!s.canFire;
    $('fire-label').textContent=({'FEU !':'FEU !','TÉLÉPORTER':'Aller','CONSTRUIRE':'Bâtir','SOIGNER':'Soigner','POSER':'Poser','POUSSER':'Pousser','FRAPPE':'Frapper'})[profile?.action]||profile?.action||'FEU !';
    const reading=profile?.power?$('power').value+' %':profile?.target?'Cible':profile?.timed?s.fuse+' s':profile?.angle?$('angle').value+'°':'Détail';
    const readout=$('shot-readout');if(readout.textContent!==reading)readout.textContent=reading;
    precisionButton.setAttribute('aria-label','Réglage précis · '+def.name+' · '+reading);
    if(lastWeapon!==s.weapon||!$('weapon-glyph').querySelector('svg')){$('weapon-glyph').innerHTML=s.icon(s.weapon);lastWeapon=s.weapon;}
    weaponButton.setAttribute('aria-label','Changer d’arme · '+def.name);
    const primary=$('weapon-name');primary.title=def.name;
    const small=primary.previousElementSibling;if(small&&small.firstChild?.nodeType===3)small.firstChild.textContent='Armes · ';
    fuseBox.hidden=!profile?.timed;
    for(const b of fuseBox.querySelectorAll('button'))b.setAttribute('aria-pressed',String(Number(b.dataset.comfortFuse)===s.fuse));
    const canMove=s.snapshot.team===s.team&&(s.snapshot.phase==='aim'||s.snapshot.retreat>0);
    quiet=!canMove;battle.classList.toggle('watching-action',quiet);
    const title=$('turn-label');if(quiet&&s.snapshot.phase!=='over')title.textContent=s.snapshot.phase==='flight'?'Impact…':'Adversaire';
    // All less-frequent controls have moved into sheets. Only real occupied bands
    // reserve camera space; a hidden sheet must never reserve the whole canvas.
    renderer.hudInsets={top:battle.querySelector('.battle-top').getBoundingClientRect().height+10,bottom:quiet?18:controls.getBoundingClientRect().height};
  }
  return {open,close,refresh,isOpen:()=>Boolean(panel),destroy(){observer.disconnect();}};
}
