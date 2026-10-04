# LOMBRIX — version 0.6.0

Jeu d’artillerie PWA : équipes de vers, terrains destructibles, solo et salons privés entre appareils distincts. Ce dépôt est exclusivement consacré à LOMBRIX. Il ne contient pas l’historique Git de Culture Gé ni des autres applications.

## Changements 0.6

**Caméra tactile.** Deux doigts déplacent le décor horizontalement et verticalement. Le pincement règle le zoom autour du milieu des doigts. Une faible variation d’écartement pendant un panoramique ne déclenche pas de zoom parasite. La visée et la puissance préparées sont conservées. Après avoir retiré un des deux doigts, le doigt restant ne reprend pas la visée : il faut terminer le geste. La barre panoramique reste disponible.

**Cadrage initial.** Le combat démarre au zoom 1,6 et directement sur le ver actif, au lieu de dériver depuis le centre de la carte. Cela donne une marge de déplacement même sur les terrains modestes et évite de commencer hors champ lorsque les premières images sont lentes.

**Armes.** Un appui sur l’arme ouvre une roue non modale de six raccourcis fixes. Un appui sur une icône l’équipe. Autre méthode : glisser depuis le bouton d’arme jusqu’à l’icône, puis relâcher. Le centre « 18 TOUTES » expose l’arsenal complet sans catégories intermédiaires. Relâcher ne tire jamais : le bouton FEU reste distinct. Les munitions, le nom et les commandes utiles à chaque équipement restent visibles.

**Couleurs.** Palettes des douze univers plus franches, ombres renforcées, brume réduite, sols et végétation plus contrastés. Les bandeaux des équipes et les commandes sont également plus lisibles. Ce sont les couleurs du moteur et des accessoires, pas un filtre CSS appliqué à une capture.

**PWA.** Cache cohérent par version. Une mise à jour en attente peut être activée depuis l’accueil, pas au milieu d’un combat. Le fichier `solo.html` est maintenant régénéré à partir de la même version que `site/`.

## Validation

Les résultats mesurés sont dans `reports/v060/` :

- `gate.json` : résultat des quatre étapes indépendantes.
- `node-tests.tap` : 43 tests du moteur, des interactions, du serveur et du cache.
- `interface.json` : 16 scénarios répartis entre WebKit et Chromium sur le vrai serveur local HTTPS.
- `two-phones/result.json` : deux processus WebKit indépendants, invitation, état prêt, tir autorisé, cratère partagé, changement de tour et rechargement.
- `offline-origin-stopped.json` : reprise du solo après arrêt réel du serveur d’origine, dans les deux moteurs.
- `session/` : publication et contrôles de l’adresse publique, lorsqu’ils ont été exécutés.

Les premiers échecs restent dans `reports/v060/history/`. La recette a notamment révélé un cadrage initial trop lent sous WebKit, corrigé avant validation. Le certificat local est explicitement approuvé par le système et par Chromium : les contrôles TLS ne sont pas désactivés.

**Limites :** WebKit Linux n’est pas un iPhone physique. Les gestes multipoints WebKit sont exercés par événements Touch simulés ; Chromium utilise également des gestes tactiles natifs CDP. Cela ne prouve pas la fluidité, l’audio, les interruptions téléphoniques ou le comportement sur toutes les versions d’iOS. Aucun essai physique Wi-Fi/4G n’est annoncé.

## Hébergement

L’adresse de la dernière publication et son statut sont consignés dans `reports/v060/session/deployment.json`. Un résultat HTTP réussi n’est pas à confondre avec l’acceptation navigateur : lire également `session/gate.json` et les rapports associés.

Le workflow `publish-v060.yml` utilise un compte Cloudflare authentifié si les secrets `CLOUDFLARE_API_TOKEN` et, si nécessaire, `CLOUDFLARE_ACCOUNT_ID` sont configurés. Sinon, il crée une démonstration temporaire. Celle-ci expire sans revendication de propriété dans le délai indiqué. Une ancienne URL de démonstration n’est pas une adresse permanente.

Les liens de revendication sont confidentiels et ne sont pas publiés dans ce dépôt. Les journaux ne contiennent que leur copie chiffrée. Ne jamais commettre un jeton API ni une clé privée.

## Développement

```sh
npm ci
npm test
node scripts/build-solo.mjs
node scripts/prepare-release.mjs
```

`site/` contient le moteur partagé, le rendu, l’audio et l’interface. `core.mjs` valide les règles des salons. `worker.mjs` fournit le serveur Cloudflare et son stockage durable. Le serveur garde l’autorité sur les tours, les dégâts et les résultats. Le HTML autonome est destiné au solo ; il ne constitue pas un serveur multijoueur.
