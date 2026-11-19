# Préprojet — Pacman 3D (Pygame / PyOpenGL)

# 1. Objectif du projet

Créer un Pacman 3D jouable en Python avec :
- un labyrinthe 3D (une map avec seed fixe obligatoire puis map générées aleatoirement)
- un joueur contrôlable
- des fantômes
- des pacgomes et super pacgomes (pour manger les fantomes)
- un fichier de config modifiable (en direct ou dans le menu)
- un système de score (avec stockage permanent)
- une condition de victoire/défaite
- HUD en jeu (minimap, score, etc...)
- victory et game over screen
- un menu
- un menu pause
- un mode cheat (pour debug ou fun)
- du son
- mettre le tout dans un project disponible sur itch.io

Technologies utilisées :
- Python
- Pygame (pygame-ce)
- PyOpenGL
- Git / GitHub (utilisation des branches)

---

# 2. MVP (Minimum Viable Product)

Le MVP représente la plus petite version jouable du jeu.

## Fonctionnalités obligatoires

- affichage d’une scène 3D (labyrinthe -> generé a partir du package)
- déplacement du joueur
- collisions avec les murs
- pellets récupérables
- score
- 1 fantôme
- minimap (map 2d en transparence dans le coin de l'ecran)
(attention gestion de l'UI necessite compatibilité avec OpenGL, pas de pygrame.draw classique)
- game over ou victoire

## Fonctionnalités bonus

- plusieurs fantomes avec comportements differents
- sons
- textures avancées
- limite de temps
- shaders
- animations
- menus
- plusieurs niveaux
- modes de difficulte

# Questions à décider ensemble

- Vue du dessus (3eme personne, vu de dos)
- Fantômes avec IA basique + variantes
- Texture ou couleurs simples: OUI (a voir plus tard pour sprites "horreur")
- Comment gérer les collisions -> Hitboxes 3d -> Cubes
---

# 3. Répartition du travail (EN COURS)

## Ben
- config (parsing)
- menu depart avec options pour changer la config, et voir les scores
(OPENGL)
- gestion high scores

## Anatole
- generer mur en 3d (modele, texture)
- generer un labyrinthe en 3d: generer maze avec le package, lire la map (eventuellement creer un objet maze)



# 5. Workflow Git

## Règles importantes

- ne jamais coder directement sur `main`
- une branche par fonctionnalité
- commit clair et précis
- tester avant de merge

# 6. Architecture des dossiers

## Exemple

```text
project/
│
├── main.py
├── engine/
│   ├── renderer.py
│   ├── camera.py
│   └── collision.py
│
├── game/
│   ├── player.py
│   ├── ghost.py
│   ├── pellets.py
│   └── map.py
│
├── assets/
│   ├── textures/
│   └── sounds/
│
└── utils/
```

---

# 11. Version minimale de secours

Si le projet devient trop ambitieux :

## Garder absolument
- labyrinthe
- joueur
- collisions
- pellets
- score
- 1 fantôme

## Retirer si nécessaire
- effets graphiques
- menus complexes
- animations avancées
- systèmes secondaires

---

