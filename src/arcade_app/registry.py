from __future__ import annotations

from arcade_app.games.asteroids.game import AsteroidsGame
from arcade_app.games.battleships.game import BattleshipsGame
from arcade_app.games.breakout.game import BreakoutGame
from arcade_app.games.connect4.game import Connect4Game
from arcade_app.games.flappy_bird.game import FlappyBirdGame
from arcade_app.games.game_2048.game import Game2048
from arcade_app.games.hangman.game import HangmanGame
from arcade_app.games.maze.game import MazeGame
from arcade_app.games.memory_match.game import MemoryMatchGame
from arcade_app.games.minesweeper.game import MinesweeperGame
from arcade_app.games.platformer.game import PlatformerGame
from arcade_app.games.pong.game import PongGame
from arcade_app.games.simon_says.game import SimonSaysGame
from arcade_app.games.snake.game import SnakeGame
from arcade_app.games.space_invaders.game import SpaceInvadersGame
from arcade_app.games.sudoku.game import SudokuGame
from arcade_app.games.tetris.game import TetrisGame
from arcade_app.games.tic_tac_toe.game import TicTacToeGame
from arcade_app.games.top_down_shooter.game import TopDownShooterGame
from arcade_app.games.whac_a_mole.game import WhacAMoleGame
from arcade_app.scenes.placeholder_game_scene import PlaceholderGameScene


GAME_REGISTRY = [
    {
        "id": "tic_tac_toe",
        "title": "Tic Tac Toe",
        "description": "Classic 3x3 strategy game with PvP and PvC play.",
        "category": "Strategy",
        "modes": ["PvP", "PvC"],
        "implemented": True,
        "scene_class": TicTacToeGame,
    },
    {
        "id": "hangman",
        "title": "Hangman",
        "description": "Guess the hidden word from themed categories before you run out of lives.",
        "category": "Word",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": HangmanGame,
    },
    {
        "id": "snake",
        "title": "Snake",
        "description": "Grow longer, avoid collisions, and chase a higher score.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": SnakeGame,
    },
    {
        "id": "connect4",
        "title": "Connect 4",
        "description": "Drop discs and connect four before your opponent does.",
        "category": "Strategy",
        "modes": ["PvP", "PvC"],
        "implemented": True,
        "scene_class": Connect4Game,
    },
    {
        "id": "battleships",
        "title": "Battleships",
        "description": "Place your fleet and hunt down the enemy ships.",
        "category": "Strategy",
        "modes": ["PvP", "PvC"],
        "implemented": True,
        "scene_class": BattleshipsGame,
    },
    {
        "id": "pong",
        "title": "Pong",
        "description": "The classic paddle rally with PvP and PvC play.",
        "category": "Arcade",
        "modes": ["PvP", "PvC"],
        "implemented": True,
        "scene_class": PongGame,
    },
    {
        "id": "breakout",
        "title": "Breakout",
        "description": "Bounce the ball, break the bricks, and protect your lives.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": BreakoutGame,
    },
    {
        "id": "memory_match",
        "title": "Memory Match",
        "description": "Flip cards, match pairs, and test your memory across difficulties.",
        "category": "Puzzle",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": MemoryMatchGame,
    },
    {
        "id": "game_2048",
        "title": "2048",
        "description": "Slide and merge tiles to reach the 2048 block.",
        "category": "Puzzle",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": Game2048,
    },
    {
        "id": "whac_a_mole",
        "title": "Whac-A-Mole",
        "description": "React quickly and hit moles before time runs out.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": WhacAMoleGame,
    },
    {
        "id": "space_invaders",
        "title": "Space Invaders",
        "description": "Defend the base, defeat alien waves, and collect shooting powerups.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": SpaceInvadersGame,
    },
    {
        "id": "asteroids",
        "title": "Asteroids",
        "description": "Pilot through space, blast asteroids, and survive each wave.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": AsteroidsGame,
    },
    {
        "id": "sudoku",
        "title": "Sudoku",
        "description": "Solve a fresh puzzle each run with notes and mistake tracking.",
        "category": "Puzzle",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": SudokuGame,
    },
    {
        "id": "minesweeper",
        "title": "Minesweeper",
        "description": "Reveal safe cells, place flags, and clear the minefield.",
        "category": "Puzzle",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": MinesweeperGame,
    },
    {
        "id": "tetris",
        "title": "Tetris",
        "description": "Stack falling pieces efficiently and clear lines for score.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": TetrisGame,
    },
    {
        "id": "simon_says",
        "title": "Simon Says",
        "description": "Memorise the sequence and repeat it correctly for as long as you can.",
        "category": "Memory",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": SimonSaysGame,
    },
    {
        "id": "flappy_bird",
        "title": "Flappy Bird",
        "description": "Navigate through pipes by flapping and survive as long as possible.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": FlappyBirdGame,
    },
    {
        "id": "top_down_shooter",
        "title": "Top-Down Shooter",
        "description": "Move, aim with the mouse, survive enemy waves, and chase a high score.",
        "category": "Action",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": TopDownShooterGame,
    },
    {
        "id": "maze",
        "title": "Maze",
        "description": "Navigate a freshly generated maze and find the exit in as few steps as possible.",
        "category": "Puzzle",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": MazeGame,
    },
    {
        "id": "platformer",
        "title": "Platformer",
        "description": "Jump across platforms, collect every coin, and reach the exit.",
        "category": "Action",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": PlatformerGame,
    },
]


def get_game_by_id(game_id: str) -> dict | None:
    for game in GAME_REGISTRY:
        if game["id"] == game_id:
            return game
    return None


def create_game_scene(game_id: str, app):
    game = get_game_by_id(game_id)
    if game is None:
        return PlaceholderGameScene(app, "Unknown Game")

    scene_class = game.get("scene_class")
    if scene_class is None:
        return PlaceholderGameScene(app, game["title"])

    return scene_class(app)