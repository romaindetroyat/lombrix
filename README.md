# LOMBRIX — version 0.6.2

Jeu d’artillerie PWA : équipes de vers, terrains destructibles, solo et salons privés entre appareils distincts. Dépôt exclusivement consacré à LOMBRIX, indépendant des autres applications.

## Ce qui change

**Premières images.** Le contrôle visuel a révélé un véritable canevas vide au démarrage sous WebKit, alors que les commandes fonctionnaient déjà. Le combat est désormais peint immédiatement lorsqu’il devient visible. Un redimensionnement inchangé ne réinitialise plus le bitmap ; un changement réel repeint le décor sans attendre le prochain cycle d’animation. Les mesures avant correction restent dans `reports/v061/first-frame/`.

**Caméra tactile.** Deux doigts déplacent le décor et règlent le zoom. Le geste fonctionne aussi lorsque le premier doigt commence sur le décor et le second sur une commande : celle-ci ne prend pas le dessus et ne tire pas. Le doigt restant ne reprend pas accidentellement la visée. La barre panoramique reste disponible. Les deux doigts uniquement sur marcher/sauter ne sont pas automatiquement interprétés comme une caméra.

**Équipements directement accessibles.** La roue a été remplacée par une bande permanente des 18 armes et outils, en ordre fixe, avec noms et munitions. Balayer horizontalement parcourt la bande sans changer d’arme ; un appui équipe immédiatement. Aucun dialogue, onglet ni confirmation supplémentaire. FEU déclenche l’action, jamais le relâchement d’un geste. Au clavier, flèches/Home/End puis Entrée permettent de choisir dans la bande.

**Couleurs et cadrage.** Sols plus colorés, bleus profonds, végétation et icônes plus saturées, accessoires moins blanchis. Le cadrage tient compte de la bande d’armes. La version est indiquée pendant le combat (`SOLO · 0.6.2` / `EN LIGNE · 0.6.2`). La définition du canevas est bornée pour limiter les allocations ; aucune mesure de fluidité sur iPhone physique n’est annoncée.

Les terrains adaptatifs, le choix de 1 à 8 vers par équipe, les bousculades, la visée descendante, les mimiques et les départs comiques sont conservés. Le moteur des dégâts et l’autorité du serveur n’ont pas été reconstruits.

## Validation

Les rapports de cette livraison sont dans `reports/v062/` :

- `node-tests.tap` : contrôles unitaires du moteur, des interactions, de l’autorité et du cache.
- `first-frame/result.json` : huit prélèvements de pixels, dès l’ouverture du combat, dans WebKit et Chromium.
- `interface.json` : commandes, gestes multipoints, sélection directe et riposte de l’IA.
- `two-phones/result.json` : invitation, état prêt, droits de tir, cratère partagé, changement de tour et reconnexion dans deux processus WebKit indépendants.
- `offline-origin-stopped.json` : reprise solo après arrêt réel du serveur d’origine.
- `gate.json` : résultat global des étapes locales ; une étape en échec empêche la validation.
- `session/` : résultats distincts de publication et de contrôle de l’adresse publique.

Les anciennes preuves et les échecs restent conservés dans `reports/v061/` et les répertoires précédents. `docs/v061/NOTES.md` et `docs/v062/NOTES.md` détaillent les correctifs.

**Limites :** WebKit Linux n’est pas un iPhone physique. Les gestes multipoints WebKit sont injectés comme snapshots TouchEvent ; Chromium utilise les entrées tactiles natives CDP. Les boutons sont actionnés via l’interface. Les tests ne valident pas toutes les versions d’iOS, l’audio réel, les appels téléphoniques ou le réseau mobile d’un appareil physique. Un HTTP 200 n’est pas à confondre avec une validation navigateur ou avec un hébergement permanent.

## Hébergement

Lire `reports/v062/session/deployment.json` pour l’adresse et le statut, ainsi que `session/gate.json` pour les résultats navigateur. Un ancien lien temporaire peut expirer et une icône déjà installée ne pointe pas automatiquement vers une nouvelle adresse.

Le workflow `publish-v062.yml` utilise le compte Cloudflare si les secrets `CLOUDFLARE_API_TOKEN` et, au besoin, `CLOUDFLARE_ACCOUNT_ID` sont configurés. Sinon, la démonstration est temporaire et doit être revendiquée dans le délai indiqué. Les liens de revendication sont conservés chiffrés, jamais publiés en clair. Ne pas commettre de jeton API ni de clé privée.

## Développement

```sh
npm ci
npm test
node scripts/build-solo.mjs
node scripts/prepare-release.mjs
```

`site/` contient le moteur partagé, le rendu, l’audio et l’interface. `core.mjs` valide les règles des salons. `worker.mjs` fournit le serveur et le stockage Cloudflare Durable Objects. Le serveur conserve l’autorité sur les tours, les dégâts et les résultats. `solo.html` est régénéré depuis la même source mais ne fournit pas de serveur multijoueur.
