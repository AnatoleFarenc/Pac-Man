# PAC-MAN — Plan du projet

## Fait

- [x] Gestion des arguments CLI (un seul argument : chemin du fichier config)
- [x] Parsing et chargement de la config (pydantic, gestion robuste des erreurs)
- [x] Parsing, stockage et chargement des high scores
- [x] Génération de labyrinthe via le package mazegenerator

---

## Ordre de développement

### 1. Map
**Responsable : Anatole**

La classe Map encapsule la sortie de mazegenerator et expose une interface claire au reste du jeu :
- Déterminer si une position en coordonnées monde est un mur
- Convertir entre coordonnées grille et coordonnées monde (via une constante CELL_SIZE)
- Fournir les positions de spawn : centre pour le joueur, coins pour les fantômes, emplacements des pacgums/super-pacgums

La représentation interne (grille étendue, basée sur les arêtes, etc.) est laissée à la décision d'Anatole.

### 2. Player
**Responsable : À définir**

- Position continue (x, y flottants) et angle de direction en coordonnées monde
- Déplacement dans 4 directions (WASD / touches directionnelles)
- Collision avec les murs via l'interface Map
- État : vies, score courant, flag d'invincibilité (pour le mode cheat)
- Respawn au centre du labyrinthe après une mort

### 3. Raycaster
**Responsable : Anatole**

- Lance des rayons depuis la position du joueur selon son angle et son FOV
- Interroge la Map à chaque étape pour détecter les murs
- Calcule la hauteur projetée de chaque tranche de mur pour chaque colonne de l'écran
- Rend la vue 3D sur la surface pygame

### 4. Pacgums
**Responsable : À définir**

- Placés dans les cellules couloir à l'initialisation du niveau (la plupart des couloirs → pacgums normaux, 4 coins → super-pacgums)
- Mangés au contact du joueur → mise à jour du score, vérification de la condition de victoire
- Super-pacgum → déclenche l'état "frightened" des fantômes pendant une durée donnée

### 5. Fantômes
**Responsable : À définir**

- 4 fantômes, un par coin, chacun avec un coin d'origine pour le respawn
- Deux comportements : chasse (normal) et fuite (frightened après un super-pacgum)
- Respawn dans leur coin d'origine après avoir été mangés (après un délai)
- Pathfinding via l'interface Map

---

## Classe Game et Machine à états

Une classe centrale `Game` possède :
- La boucle pygame principale
- Un enum `GameState` pour suivre l'état courant
- Les références à tous les objets du jeu (map, joueur, fantômes, pacgums)
- Une méthode de rendu/mise à jour par état

### Enum GameState

```
MAIN_MENU
PLAYING
PAUSED
GAME_OVER
VICTORY
FINAL_VICTORY (tous les niveaux complétés)
NAME_ENTRY
```

### Flux des états

```
MAIN_MENU → PLAYING → PAUSED → PLAYING
                     → GAME_OVER → NAME_ENTRY → MAIN_MENU
                     → VICTORY  → NAME_ENTRY → MAIN_MENU
```

### Écrans UI (méthodes de Game)

- `draw_main_menu()` — titre, démarrer, high scores, instructions, quitter
- `draw_hud()` — score, vies, niveau, temps restant (toujours visible pendant PLAYING)
- `draw_pause()` — reprendre / retour au menu principal
- `draw_game_over()` — score final
- `draw_victory()` — score final + félicitations
- `draw_final_victory()` — écran spécial à la fin du jeu (tous niveaux complétés)
- `draw_name_entry()` — saisie du nom pour le high score (max 10 caractères, alphanumérique)

---

## Progression des niveaux

- Niveau 1 : seed fixe (depuis la config)
- Niveaux 2+ : seed aléatoire
- Au moins 10 niveaux au total
- Score et vies conservés entre les niveaux
- Chaque niveau a une limite de temps (`level_max_time` depuis la config)
- Temps écoulé → conséquence configurable (recommencer le niveau ou game over)

---

## Menus

Deux classes de menu indépendantes — pas de classe de base commune, la logique de navigation est suffisamment simple pour ne pas justifier de l'héritage.

### NavigationMenu
- Une liste d'options sélectionnables navigables au clavier (haut/bas/entrée)
- Utilisé pour : menu principal, menu pause

### SettingsMenu
- Une liste de paires clé/valeur modifiables
- Utilisé pour : menu config, menu cheat

### Écrans autonomes (pas des classes menu)
- **Écran high scores** — affichage seul, pas de navigation
- **Écran de saisie du nom** — saisie de texte, modèle d'interaction fondamentalement différent

---

## Mode Cheat

Activé pendant le jeu (raccourci clavier à définir ou depuis le menu pause) :
- Invincibilité (les fantômes ne peuvent pas tuer le joueur)
- Gel des fantômes
- Passer le niveau
- Vies supplémentaires

---

## Répartition de l'équipe

| Fonctionnalité | Responsable |
|---|---|
| Config / scores / CLI | Ben |
| Map + Raycaster | Anatole |
| Player | À définir |
| Pacgums | À définir |
| Fantômes | À définir |
| Boucle de jeu + UI | À définir |
| Menus | Ben |
