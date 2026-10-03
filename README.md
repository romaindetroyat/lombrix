# LOMBRIX

Dépôt dédié au jeu d’artillerie PWA pour iPhone : solo, équipes de vers, terrains destructibles et parties privées entre appareils distincts.

Ce dépôt est indépendant de Culture Gé et des autres projets. Son historique commence ici. La migration importe uniquement les fichiers du jeu, jamais les autres applications ni leur historique Git.

## État

Migration contrôlée et correction du service worker iPhone en cours. Aucun lien de déploiement n’est déclaré opérationnel sans test de sa réponse HTTP et des parcours navigateur.

## Structure cible

- `site/` : interface PWA, moteur partagé, graphismes et son.
- `core.mjs` et `worker.mjs` : autorité de jeu et hébergement Cloudflare Durable Objects.
- Tests, documentation de reprise et configuration de déploiement propres à LOMBRIX.

Un hébergement de démonstration temporaire doit être revendiqué par son propriétaire pour devenir durable. Les liens de revendication sont des secrets et ne doivent jamais être publiés dans le dépôt.
