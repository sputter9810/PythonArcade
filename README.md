# 🎮 Python Arcade

A modular desktop arcade platform built with **Python + Pygame**, featuring ~30 polished mini-games, a unified launcher, persistent stats, and scalable architecture.

---

## 🚀 Overview

Python Arcade is a **multi-game desktop application** where players can browse, launch, and play a variety of arcade, puzzle, and skill-based games from a single interface.

The current packaged milestone is **v0.4.0**. This repository now includes the **Stage 1 platform foundations** for the next evolution from “collection of games” into a more polished arcade product:
- schema-aware save data
- launcher preferences
- player profile and global stats
- favorites
- improved library filtering, sorting, and search
- dedicated game details page

---

## 🕹️ Current Games (~30)

### 🎯 Arcade / Action
- Pong
- Breakout
- Snake
- Flappy Bird
- Endless Runner
- Frogger Clone
- Dodge the Falling Blocks
- Asteroids
- Space Invaders (with powerups)
- Top-Down Shooter
- Bullet Hell Lite
- Zombie Survival (survivor-lite system)
- Platformer

### 🧠 Puzzle / Logic
- 2048
- Minesweeper
- Sudoku (generated)
- Sliding Puzzle (generated)
- Pipe Connect (generated)
- Maze (generated)
- Memory Match (difficulty + coloured pairs)

### 🧩 Strategy / Classic
- Tic Tac Toe
- Connect 4
- Battleships (manual placement)

### 🔤 Word / Memory
- Hangman (dynamic word pool)
- Crossword (generated)
- Simon Says

### ⚡ Skill / Reaction
- Aim Trainer
- Reaction Timer
- Advanced Target Trainer
- Time Attack Challenge

---

## 💾 Current Features

- ~30 playable games
- Persistent per-game stats (scores, play counts, last played)
- Generated puzzles (Sudoku, Maze, Crossword, Pipe Connect)
- Unified UI system (header, stats, overlays)
- Packaged desktop app (PyInstaller)
- Modular architecture (scene + registry pattern)

### Stage 1 Platform Features
- Save schema versioning and migration-friendly persistence
- Launcher preference persistence
- Player profile / global stats snapshot
- Favorites system
- Better library search across title, category, description, modes, and tags
- Sorting modes:
  - alphabetical
  - most played
  - recently played
  - favorites first
- Category filtering
- Dedicated game details page
- Enriched registry metadata for launcher UX


### Stage 2A / 2B Platform Features
- Standardised run result model
- Local per-game leaderboards
- Game details leaderboard view
- Last-run and personal-best summary surfaces
- Difficulty metadata captured where games expose a difficulty field

### Stage 3 Progression Features
- Profile-based achievements system
- Cross-game progression tracking
- Achievement categories (progression, collection, skill, game-specific)
- Dedicated achievements scene
- Recent unlock feed surfaced from the active profile
- Achievement popup toasts for new unlocks
- At least 3 per-game progression achievements for each implemented game

---

## 🧱 Architecture

### Existing Core
- Scene-based navigation
- Game registry system
- Reusable UI components
- Persistence service
- Packaged desktop launcher

### Platform Layer
The product direction is now shifting toward a reusable **platform systems** layer that sits above individual games.

**Platform-wide / reusable systems**
- save schema + migration handling
- launcher preferences
- player profile + global stats
- favorites
- richer game metadata
- library filtering / sorting / search
- game details view

**Still game-specific**
- scoring logic
- mechanics
- custom progression
- future difficulty adoption
- future seeded/replay support

---

## 📁 Project Structure

```text
src/
  arcade_app/
    core/
    games/
    platform/
    scenes/
    ui/
    registry.py
tests/
```

### Important Files After Stage 1
- `src/arcade_app/core/save_data.py`
  - schema-aware save data manager
  - profile, favorites, launcher preferences
- `src/arcade_app/platform/library.py`
  - reusable library filtering, sorting, stats formatting helpers
- `src/arcade_app/registry.py`
  - enriched metadata normalisation
- `src/arcade_app/scenes/game_select_scene.py`
  - upgraded arcade library UX
- `src/arcade_app/scenes/game_details_scene.py`
  - dedicated details page for each game
- `src/arcade_app/scenes/main_menu_scene.py`
  - profile snapshot surfaced on the home screen

---

## 🎮 Launcher Controls (Stage 1)

### Main Menu
- `1` → Open arcade library
- `2` → Open settings
- `3` → Open credits
- `4` → Open details for last played game
- `Esc` → Quit

### Arcade Library
- `WASD / Arrow Keys` → Move selection
- `Enter / Space` → Launch selected game
- `I / Tab` → Open game details
- `F` → Favorite / unfavorite selected game
- `C` → Cycle category filter
- `S` → Cycle sort mode
- `T` → Toggle favorites-only filter
- `R` → Reset filters
- `/` → Focus search
- `Q / E` or `PageUp / PageDown` → Change page
- `Esc` → Return to main menu

### Game Details
- `Enter / Space` → Launch game
- `F` → Favorite / unfavorite
- `Backspace / Esc` → Return

---

# 🚀 Product Roadmap

## Stage 1 — Platform Foundation and Launcher Upgrade
**Goals**
- strengthen save/config foundations
- add profile/global stats
- improve library UX
- support favorites and better discoverability

**Why this stage comes first**
- later systems depend on stronger persistence and richer metadata
- improves product feel without destabilising existing games

**Included systems**
- save schema v2
- launcher preferences
- favorites
- player profile snapshot
- registry metadata enrichment
- search, filter, sort upgrades
- game details page

---

## Stage 2 — Standardised Run Results, Difficulty, and Local Leaderboards
**Goals**
- formalise what a “run” is
- standardise post-game data
- add local leaderboards
- improve result / game-over flow consistency
- introduce optional standard difficulty support where appropriate

**Why this stage belongs here**
- depends on Stage 1 persistence and launcher metadata
- gives immediate product polish while remaining practical

**Likely systems**
- shared `RunResult` model
- leaderboard storage/querying
- shared result summary UI
- difficulty support contract for games that actually suit it

---

## Stage 3 — Achievements and Progression Layer
**Goals**
- create a real cross-game progression loop
- add achievements and unlock tracking
- surface profile progression in launcher and post-run flows

**Why this stage comes after Stage 2**
- achievements need stable stats, standardized run data, and a stronger profile layer first

**Likely systems**
- achievement definitions + unlock state
- global/platform achievements
- curated game-specific achievements
- unlock notification UI
- profile achievements page/panel

---

## Stage 4 — Advanced Meta Systems and Product Finish

Stage 4 now begins with a practical meta-systems slice:
- seeded daily challenges
- daily challenge history per local profile
- seeded run metadata surfaced in run summaries and game details
- launcher and menu shortcuts for challenge access

**Goals**
- add standout portfolio/product systems
- explore daily challenges, seeded runs, and selective replay support
- improve overall product readiness and uniqueness

**Why this stage is last**
- these systems depend on stable foundations and should remain opt-in where complexity is high

**Likely systems**
- daily challenge framework
- seeded run launch support
- replay prototype for carefully chosen games only
- final product polish pass

---

## 🧪 Testing Focus for Stage 1

When implementing or verifying Stage 1, concentrate on:
- loading old save data without breaking existing stats
- favorite toggle persistence
- launcher preference persistence
- filtering/sorting correctness
- details page metadata correctness
- profile summary accuracy
- unchanged launch flow for existing games

A manual checklist is included separately with the Stage 1 delivery files.

---

## 👤 Author

Sam Briggs


## 🏆 Stage 3 Focus

Stage 3 introduces the first real progression layer for the arcade platform. The goal is to make the launcher feel like a connected product rather than a folder of disconnected games.

Current Stage 3 scope:
- achievement definitions live in `src/arcade_app/platform/achievements.py`
- unlocked achievements are stored per local profile
- main menu and details pages surface progression information
- the achievements scene acts as a dedicated profile progression view

Planned later Stage 3 expansions:
- unlock popups / notifications
- more game-specific achievements
- richer progression milestones
- achievement-aware run summaries
