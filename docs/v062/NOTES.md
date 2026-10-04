# LOMBRIX 0.6.2 — premières images visibles

Cette livraison conserve la barre permanente des 18 armes, les couleurs plus franches et le geste à deux doigts couvrant le décor et une commande, introduits dans 0.6.1.

Un contrôle des pixels a confirmé que le canevas WebKit restait vide dans les deux premiers prélèvements au démarrage, puis affichait le décor au prélèvement suivant. Les dimensions CSS étaient déjà correctes. Le test initial limité aux commandes ne détectait pas ce défaut. Les mesures originales restent dans `reports/v061/first-frame/result.json`.

Le canevas est désormais peint immédiatement quand le combat devient visible. Un redimensionnement identique ne réinitialise plus inutilement son bitmap ; un changement effectif de dimensions repeint le contenu sans attendre une prochaine image d'animation. Aucune modification des dégâts, de la balistique ou des règles réseau.

La validation 0.6.2 ajoute huit prélèvements de pixels (quatre par moteur) dès l'ouverture du combat, avant tout geste sur le terrain, aux contrôles d'interface, au test entre deux processus WebKit et au rechargement hors ligne. WebKit Linux n'est pas un iPhone physique. Une adresse temporaire Cloudflare n'est toujours pas un hébergement permanent.
