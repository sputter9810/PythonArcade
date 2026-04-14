# Architecture

## Goal

Build a scalable desktop arcade application in Python using Pygame, with a clean launcher and a growing library of mini-games.

## Core design principles

1. **Single application shell**
   - One executable/app entry point
   - One launcher
   - One settings flow
   - One shared visual system

2. **Scene-driven structure**
   - Each screen is a scene
   - Examples: main menu, game select, settings, credits, individual games
   - The SceneManager is responsible for swapping scenes

3. **Game modules are isolated**
   - Each game gets its own folder
   - Game logic must be separate from rendering
   - Shared UI and theme code stay outside game folders

4. **Launcher is registry-driven**
   - The game select screen reads from `registry.py`
   - Adding a new game should not require rewriting the launcher grid

5. **Shared UI system**
   - Buttons, cards, spacing, fonts, and screen regions come from shared UI modules
   - Avoid ad hoc positioning to prevent overlap

## Base module responsibilities

### `app.py`
Owns application lifecycle, window setup, and the main loop.

### `core/scene_manager.py`
Controls scene transitions and current scene execution.

### `core/scene_base.py`
Defines the shared interface for all scenes.

### `core/game_base.py`
Defines the shared interface for all playable games.

### `registry.py`
Defines game metadata for launcher display and future dynamic loading.

### `ui/theme.py`
Stores design tokens for colour, spacing, radius, and typography.

### `ui/screen.py`
Defines standard page regions such as header, content, and footer.

## Future game structure

Each game should follow this layout:

```text
games/<game_name>/
├── game.py
├── logic.py
├── render.py
└── data.py
```

### Purpose of each file

- `game.py` — scene entry point for the game
- `logic.py` — rules, state checks, scoring, AI, board validation
- `render.py` — drawing helpers and screen presentation
- `data.py` — constants, word lists, boards, levels, config values

## Scalability plan

The app should be able to grow past 16 games with minimal rework.

Required scalable elements:
- dynamic registry reading
- paginated or scrollable launcher in the future
- reusable shared settings
- centralised save/high-score storage
- consistent per-game interface

## Suggested milestones

1. Foundation shell
2. Launcher UI
3. First simple games
4. Shared overlays and pause menu
5. Save data / high scores
6. Packaging and release
