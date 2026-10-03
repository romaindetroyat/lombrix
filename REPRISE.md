# Reprise — LOMBRIX 0.5.2

## Destination autorisée

Tout le développement et tous les déploiements de LOMBRIX doivent rester dans `romaindetroyat/lombrix`. Ne pas utiliser Culture Gé ni une branche d’un autre projet. L’historique du dépôt est indépendant ; voir `MIGRATION.json`.

## Dernière publication demandée — 3 octobre 2026

- Code déployé : `ef958f7e843e991069b81ce534cbd859cacbaf12`.
- Version de l’application et de l’autorité : **0.5.2**.
- URL de session : **https://lombrix.tough-archduke.workers.dev**.
- Déploiement demandé à 17:28:37 UTC.
- Échéance conservatrice de revendication : **18:28 UTC, soit 20:28 à Paris, le 3 octobre 2026**. Sans revendication achevée, le compte temporaire et ses ressources expirent. Ne pas affirmer que cette URL demeure disponible après l’échéance sans la revérifier.
- Workflow public : `37140630534`, succès. Rapport HTTP : `reports/session/deployment.json`.
- **Parcours public WebKit réussi** : deux processus indépendants, invitation, préparation, tir, autorité des équipes, cratère partagé, passage du tour et rechargement conservant l’identité. Rapport : `reports/session/public-two-phones/result.json`.
- Le lien de revendication est transmis uniquement au propriétaire, hors dépôt. `reports/session/claim.encrypted.json` n’est pas le lien utilisable et ne doit pas être remplacé par un secret en clair.

## Vérifications et limites

10 tests serveur/cache réussis dans ce dépôt. Solo, riposte IA et rechargement validés sous WebKit et Chromium en local. Recette multijoueur réalisée d’abord en HTTPS local puis sur l’URL publique. Ne pas présenter ces tests comme des essais sur iPhone physique ni comme un test de charge.

Les anciens rapports d’échec restent conservés. Les 401 de la première recette HTTP WebKit provenaient des cookies Secure utilisés sur HTTP local. Le test HTTPS utilise un vrai certificat local approuvé et les cookies de production inchangés. Le défaut initial de réponse de navigation redirigée est corrigé dans `site/sw.js` par `cleanResponse`.

## Suite

1. Vérifier que le propriétaire a terminé la revendication Cloudflare et confirmer l’URL et le compte conservés.
2. Relier les prochains déploiements à son compte Cloudflare autorisé ; ne pas recréer une succession de sessions temporaires.
3. Faire la recette physique sur deux iPhone : Safari/paysage, ajout à l’accueil, audio après toucher, interruptions/reconnexion, réseaux différents.
4. Conserver l’intégralité des améliorations de jeu 0.5.1 présentes dans `site/` et avancer par étapes validées.

`solo.html` est l’ancien export autonome 0.5.1. Le site publié utilise `site/`, et non l’ancienne application Lovable 0.3.1.
