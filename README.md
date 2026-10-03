# LOMBRIX — jeu PWA pour iPhone

Dépôt **exclusivement consacré à LOMBRIX**, indépendant de Culture Gé et des autres applications. La migration est terminée : aucun historique Git des autres projets n’a été importé. `MIGRATION.json` conserve les empreintes des fichiers transférés.

## Version

**0.5.2** : jeu issu de la 0.5.1, avec correction de la navigation/cache iPhone. Solo contre l’ordinateur, terrains destructibles, commandes tactiles, ceinture d’armes, caméra panoramique, et serveur autoritaire pour les salons privés. Le fichier historique `solo.html` reste l’export autonome 0.5.1 ; l’application publiée provient de `site/`.

## Ouvrir le jeu

La dernière session demandée et son URL sont enregistrées dans [`reports/session/deployment.json`](reports/session/deployment.json). Ne pas confondre l’adresse GitHub du code avec l’adresse du jeu.

Une publication Cloudflare temporaire expire après 60 minutes si son propriétaire ne termine pas la revendication dans Cloudflare. Son lien de revendication est privé : il est transmis au propriétaire hors du dépôt. Seule sa version chiffrée peut figurer dans les rapports. Aucun jeton d’administration ni clé privée ne doit être ajouté à Git.

Sur iPhone : ouvrir l’URL du jeu dans Safari, utiliser le paysage, puis « Jouer en solo ». Pour un duel : « Défier un ami », partager l’invitation, attendre que chaque joueur soit prêt, puis lancer la bataille. Chaque personne utilise son propre appareil.

## Validation réellement effectuée

- **10 tests de l’adaptateur serveur et du cache PWA réussis** (`npm test`). Ce nombre ne désigne pas la totalité des tests historiques des anciennes archives.
- Solo, tir, riposte IA et rechargement avec service worker : exécutés sous WebKit et Chromium, voir `reports/local/browser.json`.
- **Duel complet d’acceptation sous deux processus WebKit indépendants, en HTTPS local : réussi.** Invitation, préparation des joueurs, identités distinctes, refus d’une commande adverse, tir, cratère partagé, passage du tour et rechargement sans perdre sa place. Voir `reports/two-phones-https/result.json`.
- Le premier essai local HTTP échouait avec des réponses 401 : les cookies de session `Secure` n’étaient pas renvoyés par WebKit. La recette utilise désormais un vrai HTTPS local avec certificat de test approuvé, sans supprimer `Secure`, sans changer les règles du jeu et sans simuler l’authentification. L’échec initial reste dans `reports/two-phones/`.
- La validation de l’adresse publique est **distincte** de la recette locale : consulter `reports/session/public-two-phones/result.json`. Une réponse HTTP 200 ne suffit pas à déclarer le parcours navigateur réussi. Des protections Cloudflare peuvent bloquer le navigateur automatisé ; elles ne sont pas contournées.

**Aucun de ces essais ne remplace une recette sur iPhone physique.** L’ergonomie réelle, les interruptions iOS et les performances prolongées restent à mesurer.

## Structure

- `site/` : interface, moteur partagé, rendu, audio, manifeste et service worker.
- `core.mjs` : règles des salons et validation des actions.
- `worker.mjs` : hébergement Cloudflare et persistance via Durable Object.
- `*.test.mjs` : tests serveur et service worker.
- `scripts/` : vérification, préparation et publication.
- `.github/workflows/` : étapes indépendantes ; les erreurs restent visibles et les rapports sont sauvegardés.
- `reports/` : résultats mesurés, avec contexte et limites.

## Développement et publication durable

```sh
npm ci
npm test
npx wrangler dev --local --local-protocol https
```

Le développement local HTTPS nécessite d’approuver un certificat local. En production, utiliser le certificat public de l’hébergeur. Ne pas désactiver les protections du cookie pour faire passer un test HTTP.

Après rattachement du compte Cloudflare par le propriétaire :

```sh
npx wrangler login
npx wrangler deploy
```

Le déploiement durable utilise un compte autorisé, sans `--temporary`. Les actions permanentes devront utiliser un secret limité à ce déploiement, jamais un secret inclus dans les fichiers du jeu.

## Limites actuelles

Le serveur vise les essais privés, avec 20 salons au maximum dans une autorité sérialisée. Ce n’est pas une architecture validée pour une exploitation à grande échelle. Les versions temporaires ne constituent pas un engagement de disponibilité. Les autres dépôts ne doivent jamais servir de destination de publication pour LOMBRIX.
