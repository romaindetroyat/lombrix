# LOMBRIX — version 0.6.1

Jeu d’artillerie PWA : équipes de vers, terrains destructibles, solo et salons privés entre appareils distincts. Dépôt exclusivement consacré à LOMBRIX, sans l’historique Git des autres applications.

## Changements 0.6.1

**Caméra à deux doigts.** Un défaut a été reproduit en 0.6.0 : premier doigt sur le décor et second sur une commande, la caméra restait presque immobile et la visée changeait. Le suivi prend désormais en compte l’ensemble des contacts de l’arène, même si le second doigt arrive sur une commande. Le geste de caméra prend priorité et ne déclenche pas de tir. Après retrait d’un doigt, le doigt restant ne reprend pas la visée. Les deux doigts réservés aux boutons marcher/sauter ne sont pas automatiquement interprétés comme un panoramique.

**Armes accessibles directement.** La roue est remplacée par une bande permanente des 18 équipements, en ordre fixe. Balayer horizontalement parcourt les armes ; un appui équipe. Le balayage ne sélectionne pas accidentellement une arme. Aucun dialogue, catégorie ni bouton de confirmation. Le nom, les munitions et l’équipement sélectionné restent visibles. FEU reste distinct. Au clavier, flèches/Home/End puis Entrée permettent aussi de choisir dans la bande.

**Couleurs.** Sols plus colorés, ciel bleu plus soutenu, végétation plus saturée, accessoires moins blanchis, icônes plus franches. Les changements concernent le moteur et les éléments graphiques, pas un filtre sur une capture.

**Lisibilité et cadrage.** Le cadrage prend en compte l’espace occupé par la bande d’équipements et la barre panoramique. La version s’affiche pendant le combat (`SOLO · 0.6.1` / `EN LIGNE · 0.6.1`) pour distinguer les anciennes installations. La définition maximale du canevas est bornée ; aucune mesure de fréquence d’images sur iPhone physique n’est revendiquée.

Les terrains adaptatifs, le choix de 1 à 8 vers par équipe, les collisions entre vers, la visée descendante, les mimiques et les séquences de mort sont conservés. Le moteur des dégâts et l’autorité du serveur n’ont pas été reconstruits.

## Comment jouer

- Un doigt sur le décor règle la visée. La variation de distance ajuste progressivement la puissance ; relever puis reposer le doigt conserve la charge.
- Deux doigts sur le décor déplacent la caméra. Écarter/rapprocher règle le zoom. La barre panoramique permet aussi d’explorer horizontalement sans dézoomer.
- Parcourir la bande d’armes puis toucher une icône équipe l’arme. Le bouton FEU déclenche l’action.
- En ligne, chaque joueur ouvre le lien d’invitation sur son propre appareil.

## Validation mesurée

Les résultats de cette version sont dans `reports/v061/` :

- `baseline-reproduction.json` : comparaison du geste défectueux en 0.6.0 et de sa correction en 0.6.1, sous Chromium tactile.
- `node-tests.tap` : 43 contrôles unitaires du moteur, des interactions, de l’autorité et du cache.
- `interface.json` : 15 scénarios d’interface répartis entre WebKit et Chromium sur le vrai serveur local HTTPS.
- `two-phones/result.json` : invitation, état prêt, droits de tir, cratère partagé, changement de tour et rechargement dans deux processus WebKit indépendants.
- `offline-origin-stopped.json` : reprise solo après arrêt réel du serveur d’origine.
- `gate.json` : résultat global ; une étape en échec empêche la validation.
- `session/` : résultats de publication et de vérification sur l’adresse publique, lorsqu’ils ont été exécutés.

Les rapports des versions antérieures sont conservés dans leurs répertoires. `docs/v061/NOTES.md` précise les modifications et la méthode.

**Limites :** les essais utilisent WebKit et Chromium sous Linux, pas des iPhone physiques. Les gestes multipoints WebKit sont injectés comme snapshots TouchEvent ; Chromium utilise les entrées tactiles natives CDP. Les boutons sont actionnés via l’interface. Cela ne valide pas la fluidité, l’audio ou les interruptions téléphoniques sur toutes les versions d’iOS. Le test hors ligne arrête réellement le serveur local, sans prétendre actionner le mode avion d’un téléphone.

## Hébergement

Consulter `reports/v061/session/deployment.json` pour l’adresse et le statut de la publication. Un HTTP 200 ne suffit pas : consulter également `session/gate.json` et les rapports navigateur.

Le workflow `publish-v061.yml` utilise un compte Cloudflare authentifié si les secrets `CLOUDFLARE_API_TOKEN` et, au besoin, `CLOUDFLARE_ACCOUNT_ID` sont configurés. Sinon, il crée une démonstration temporaire, qui expire sans revendication dans le délai indiqué. Une ancienne URL temporaire n’est pas un lien permanent, et une ancienne icône installée ne pointe pas automatiquement vers un nouveau déploiement.

Les liens de revendication ne sont pas publiés en clair dans le dépôt. Ne jamais commettre un jeton API ni une clé privée.

## Développement

```sh
npm ci
npm test
node scripts/build-solo.mjs
node scripts/prepare-release.mjs
```

`site/` contient le moteur partagé, le rendu, l’audio et l’interface. `core.mjs` valide les règles des salons. `worker.mjs` fournit le serveur et son stockage Cloudflare Durable Objects. Le serveur conserve l’autorité sur les tours, les dégâts et les résultats. `solo.html` est régénéré depuis la même source mais ne fournit pas de serveur multijoueur.
