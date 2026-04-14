# 🎮 Python Arcade

A modular desktop arcade application built with **Python + Pygame**, featuring a growing collection of classic and modern mini-games, a unified launcher, persistent stats, and a clean, scalable architecture.

---

## 🚀 Overview

Python Arcade is designed as a **multi-game platform**, allowing players to launch and play a variety of games from a single interface. The project focuses on:

* Clean UI/UX design
* Scalable architecture (scene management + registry pattern)
* Persistent player data (stats, settings, last played)
* Expandability for future games

---

## 🕹️ Current Games (16)

* Tic Tac Toe
* Hangman
* Snake
* Connect 4
* Battleships
* Pong
* Breakout
* Memory Match
* 2048
* Whac-A-Mole
* Space Invaders
* Asteroids
* Sudoku
* Minesweeper
* Tetris
* Simon Says

---

## 🧱 Architecture Highlights

* **Scene-based system** (Main Menu, Game Select, Individual Games)
* **Game Registry** for dynamic loading
* **Reusable UI components** (cards, buttons, layout system)
* **Persistent storage** for:

  * Play counts
  * High scores
  * Last played game
  * User settings

---

## 💾 Features

* 🎮 16 playable games
* 🧠 Persistent stats & progression
* ⚙️ Configurable settings
* 🖥️ Packaged desktop application (PyInstaller)
* 🎯 Keyboard and mouse support across all games
* 📊 Game metadata and tracking

---

## 🛠️ Tech Stack

* Python 3.11+
* Pygame
* PyInstaller (for packaging)

---

## 📦 Running the Project

### Development

```bash
pip install -r requirements.txt
python run.py
```

### Packaged Build

Navigate to:

```
dist/Arcade/
```

Then run:

```
Arcade.exe
```

---

## 📁 Project Structure

```
src/
  arcade_app/
    core/        # Scene manager, base classes
    games/       # Individual game implementations
    scenes/      # Menu and navigation scenes
    ui/          # Reusable UI components
    services/    # Persistence and utilities
    registry.py  # Game registry system
```

---

## 🧪 Future Roadmap (Next 16 Games)

The goal is to expand from **16 → 32 games** with a focus on variety, mechanics, and technical depth.

### 🟢 Core Arcade

* Flappy Bird
* Endless Runner
* Frogger Clone
* Dodge the Falling Blocks

### 🔵 Skill & Reaction

* Aim Trainer
* Reaction Timer
* Advanced Target Trainer (Whac-a-Mole variant)
* Time Attack Challenge

### 🟣 Puzzle & Logic

* Maze Generator + Solver
* Sliding Puzzle (15 Puzzle)
* Crossword / Word Puzzle
* Pipe Connection (Flow-style)

### 🔴 Action / Shooter

* Top-Down Shooter
* Bullet Hell Lite
* Zombie Survival

### 🟡 Physics / Platforming

* Basic Platformer

---

## 🎯 Project Goals

* Build a **polished, extensible game platform**
* Demonstrate **real-world software engineering practices**
* Showcase **UI consistency and system design**
* Create a **portfolio-ready desktop application**

---

## 📌 Future Improvements

* Sound system (music + SFX)
* Global leaderboard
* Recently played section on main menu
* Difficulty scaling across games
* Additional polish and UI animations

---

## 👤 Author

**Sam Briggs**
Software Engineering Student (UON)

---

## 🙌 Acknowledgements

* Pygame community
* Open-source contributors
* ChatGPT (development assistance, planning, debugging)

---

## 📜 License

This project is for educational and portfolio purposes.
