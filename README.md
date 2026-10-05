# LOMBRIX — version 0.7.0

Jeu d’artillerie PWA : équipes de vers, terrains destructibles, solo et salons privés entre appareils distincts. Ce dépôt est exclusivement consacré à LOMBRIX, indépendant des autres applications.

## Interface lisible, plus de place pour jouer

La bande permanente des 18 armes, les curseurs de tir et la barre panoramique ne sont plus affichés simultanément. Le terrain reste visible entre une ligne d’état et les commandes de pouce.

- **Armes :** toucher le bouton de l’arme équipée ouvre un tiroir temporaire de grandes vignettes, avec les noms complets et les munitions. Faire défiler verticalement, puis toucher une arme : elle est équipée et le tiroir se ferme. Pas de catégorie intermédiaire, pas de confirmation supplémentaire. Le chronomètre continue.
- **Visée :** le doigt sur le terrain conserve le réglage direct de l’angle et de la puissance. Le bouton Visée donne accès aux curseurs plus grands et à la mèche pour les grenades. FEU reste une action distincte.
- **Caméra :** deux doigts déplacent le décor ; le pincement zoome. Le bouton Caméra ouvre les réglages de zoom, la barre panoramique et le recentrage. Les manipulations de caméra ne modifient pas la visée.
- **Lisibilité :** noms des armes à 17 pixels CSS par défaut, contre 9 pixels dans l’ancienne bande. Menu → Lisibilité propose 20 pixels pour les textes principaux. Les boutons principaux ont des cibles tactiles d’au moins 44 × 44 pixels CSS dans les formats contrôlés.
- **Observation :** les commandes du bas se retirent pendant le tour adverse et après la fin de la retraite, puis reviennent au tour du joueur. Le menu et la caméra restent disponibles. La version, le tour et le terrain restent consultables dans le menu.

À 844 × 390, la hauteur centrale sans barre d’interface passe de **151 à 230 pixels**, soit environ 52 % de plus. Il s’agit d’une mesure de disposition dans un navigateur, hors marges physiques et chrome de Safari ; ce n’est pas une mesure sur iPhone réel ni un pourcentage de gain de performances.

Les terrains adaptatifs, 1 à 8 vers par équipe, les bousculades, tirs descendants, mimiques et éliminations sont conservés. Le moteur des dégâts et l’autorité du serveur ne sont pas reconstruits.

## Validation et limites

`reports/v070/gate.json` et `interface.json` conservent les contrôles de la version HTML autonome dans WebKit et Chromium sur cinq formats (petit paysage, paysage, portrait et bureau). `node-tests.tap` contient les 43 tests unitaires. Les contrôles de l’adresse publique sont distincts et ne sont pas déduits de ces tests locaux.

Les gestes multipoints WebKit sont injectés comme snapshots TouchEvent ; Chromium utilise les entrées tactiles natives CDP. Les boutons sont actionnés via l’interface. WebKit Linux n’est pas un iPhone physique : la fluidité, le son réel, les appels téléphoniques et les particularités de toutes les versions d’iOS ne sont pas certifiés par ces tests.

Les anciennes preuves, y compris leurs échecs, restent dans les répertoires précédents. `docs/v070/NOTES.md` détaille la présente évolution. `BUILD.json` décrit les fichiers exacts de la livraison.

## Hébergement stable

**Adresse du jeu : https://lombrix.romaindetroyat.workers.dev/**

Le propriétaire a relié directement ce dépôt à Cloudflare Workers Builds. La production utilise la branche `main`, `npm test` et `npx wrangler deploy`. Ne pas lancer les anciens workflows de démonstration temporaire pour remplacer ce déploiement.

Une nouvelle version est disponible après réussite du déploiement Cloudflare. Le service worker ne remplace pas une partie en cours ; une mise à jour en attente s’active depuis l’accueil. Il n’est pas nécessaire d’effacer les sauvegardes Safari pour une mise à jour normale.

## Développement

```sh
npm ci
npm test
node scripts/build-solo.mjs
node scripts/prepare-release.mjs
```

`site/` contient le moteur partagé, le rendu, l’audio et l’interface. `comfort.js` et `comfort.css` définissent l’interface à divulgation progressive. `core.mjs` valide les règles des salons ; `worker.mjs` fournit le serveur et le stockage Cloudflare Durable Objects. Le serveur conserve l’autorité sur les tours, dégâts et résultats. `solo.html` est régénéré depuis la même source mais ne fournit pas de serveur multijoueur.
