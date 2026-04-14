from __future__ import annotations

from arcade_app.games.asteroids.game import AsteroidsGame
from arcade_app.games.battleships.game import BattleshipsGame
from arcade_app.games.breakout.game import BreakoutGame
from arcade_app.games.connect4.game import Connect4Game
from arcade_app.games.game_2048.game import Game2048
from arcade_app.games.hangman.game import HangmanGame
from arcade_app.games.memory_match.game import MemoryMatchGame
from arcade_app.games.minesweeper.game import MinesweeperGame
from arcade_app.games.pong.game import PongGame
from arcade_app.games.simon_says.game import SimonSaysGame
from arcade_app.games.snake.game import SnakeGame
from arcade_app.games.space_invaders.game import SpaceInvadersGame
from arcade_app.games.sudoku.game import SudokuGame
from arcade_app.games.tetris.game import TetrisGame
from arcade_app.games.tic_tac_toe.game import TicTacToeGame
from arcade_app.games.whac_a_mole.game import WhacAMoleGame
from arcade_app.scenes.placeholder_game_scene import PlaceholderGameScene


GAME_REGISTRY = [
    {
        "id": "tic_tac_toe",
        "title": "Tic Tac Toe",
        "description": "Classic 3x3 strategy.",
        "category": "Strategy",
        "modes": ["PvP", "PvC"],
        "implemented": True,
        "scene_class": TicTacToeGame,
    },
    {
        "id": "hangman",
        "title": "Hangman",
        "description": "Guess the hidden word.",
        "category": "Word",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": HangmanGame,
    },
    {
        "id": "snake",
        "title": "Snake",
        "description": "Grow longer and survive.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": SnakeGame,
    },
    {
        "id": "connect4",
        "title": "Connect 4",
        "description": "Four in a row wins.",
        "category": "Strategy",
        "modes": ["PvP", "PvC"],
        "implemented": True,
        "scene_class": Connect4Game,
    },
    {
        "id": "battleships",
        "title": "Battleships",
        "description": "Hunt the enemy fleet.",
        "category": "Strategy",
        "modes": ["PvP", "PvC"],
        "implemented": True,
        "scene_class": BattleshipsGame,
    },
    {
        "id": "pong",
        "title": "Pong",
        "description": "The original arcade rally.",
        "category": "Arcade",
        "modes": ["PvP", "PvC"],
        "implemented": True,
        "scene_class": PongGame,
    },
    {
        "id": "breakout",
        "title": "Breakout",
        "description": "Smash the brick wall.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": BreakoutGame,
    },
    {
        "id": "memory_match",
        "title": "Memory Match",
        "description": "Flip and find pairs.",
        "category": "Puzzle",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": MemoryMatchGame,
    },
    {
        "id": "game_2048",
        "title": "2048",
        "description": "Merge your way to 2048.",
        "category": "Puzzle",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": Game2048,
    },
    {
        "id": "whac_a_mole",
        "title": "Whac-A-Mole",
        "description": "Hit fast, score faster.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": WhacAMoleGame,
    },
    {
        "id": "space_invaders",
        "title": "Space Invaders",
        "description": "Defend against alien waves.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": SpaceInvadersGame,
    },
    {
        "id": "asteroids",
        "title": "Asteroids",
        "description": "Pilot, shoot, and survive.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": AsteroidsGame,
    },
    {
        "id": "sudoku",
        "title": "Sudoku",
        "description": "Logic puzzle challenge.",
        "category": "Puzzle",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": SudokuGame,
    },
    {
        "id": "minesweeper",
        "title": "Minesweeper",
        "description": "Clear the grid safely.",
        "category": "Puzzle",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": MinesweeperGame,
    },
    {
        "id": "tetris",
        "title": "Tetris",
        "description": "Stack pieces efficiently.",
        "category": "Arcade",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": TetrisGame,
    },
    {
        "id": "simon_says",
        "title": "Simon Says",
        "description": "Repeat the colour sequence.",
        "category": "Memory",
        "modes": ["Solo"],
        "implemented": True,
        "scene_class": SimonSaysGame,
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