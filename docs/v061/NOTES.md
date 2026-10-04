# LOMBRIX 0.6.1 — correction tactile et sélection directe

## Demande
Deux doigts pour déplacer la caméra sur iPhone, rendu moins pastel sur Mac et iPhone, sélection des armes plus directe. Travail exclusivement dans `romaindetroyat/lombrix`, à partir de la version 0.6.0.

## Défaut reproduit
Dans Chromium tactile, le premier doigt sur le décor et le second sur FEU ne produisaient pratiquement aucun panoramique (0,45 unité) et modifiaient la visée en 0.6.0. Le même parcours sur 0.6.1 déplace la caméra de 92,18 unités, conserve angle et puissance et ne tire pas. Mesures : `reports/v061/baseline-reproduction.json`. Ce scénario n'est pas une reproduction sur l'iPhone physique de l'utilisateur.

Le suivi des contacts s'effectue maintenant au niveau de toute l'arène. Un geste à deux doigts comprenant le décor prend priorité sur les commandes recouvertes. Deux doigts uniquement sur les commandes de déplacement/saut ne sont pas automatiquement interprétés comme un panoramique. Le doigt restant après un geste caméra ne reprend pas la visée. Les clics synthétiques après le geste sont filtrés ; un nouvel appui volontaire reste utilisable.

## Équipements
La roue est remplacée par une bande horizontale permanente des 18 équipements, en ordre fixe, avec nom et munitions. Un balayage parcourt la bande sans changer d'arme ; un appui équipe immédiatement. Aucun dialogue, onglet, ni confirmation d'équipement. FEU reste séparé. Les flèches/Home/End et Entrée fonctionnent dans la barre au clavier. Le bouton de l'arme équipée recentre la bande sur cette arme.

## Graphismes et visibilité
Sols plus colorés, tons froids plus profonds, végétation et accessoires moins blanchis, icônes plus saturées. Le cadrage tient compte de la bande d'armes et de la barre de caméra. La définition maximale du canevas est plafonnée pour limiter les allocations sur mobile ; aucune mesure de fréquence d'images sur iPhone physique n'est revendiquée.

La version apparaît également pendant le combat (`SOLO · 0.6.1` / `EN LIGNE · 0.6.1`). Un export HTML n'est pas une mise à jour du site déjà installé. Le serveur et la logique des dégâts n'ont pas été reconstruits.

## Validation et limites
Les résultats de cette livraison sont dans `reports/v061/`. Chaque étape conserve son résultat ; le contrôle global échoue si une étape échoue. Chromium utilise ses entrées tactiles natives via CDP ; les trajectoires multi-touch WebKit sont injectées sous forme de snapshots TouchEvent, tandis que les boutons utilisent les appuis Playwright. Aucun essai sur iPhone physique, Safari iOS installé ou réseau mobile réel n'est simulé dans les comptes rendus.

Les tests d'invitation utilisent deux processus WebKit indépendants, le vrai Worker en HTTPS et ses cookies Secure/HttpOnly. Le test hors ligne arrête réellement le serveur d'origine. Les contrôles publics sont distincts des essais locaux.
