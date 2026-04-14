from __future__ import annotations

from arcade_app.games.advanced_target_trainer.game import AdvancedTargetTrainerGame
from arcade_app.games.aim_trainer.game import AimTrainerGame
from arcade_app.games.asteroids.game import AsteroidsGame
from arcade_app.games.battleships.game import BattleshipsGame
from arcade_app.games.breakout.game import BreakoutGame
from arcade_app.games.connect4.game import Connect4Game
from arcade_app.games.dodge_falling_blocks.game import DodgeFallingBlocksGame
from arcade_app.games.endless_runner.game import EndlessRunnerGame
from arcade_app.games.flappy_bird.game import FlappyBirdGame
from arcade_app.games.frogger_clone.game import FroggerCloneGame
from arcade_app.games.game_2048.game import Game2048
from arcade_app.games.hangman.game import HangmanGame
from arcade_app.games.maze.game import MazeGame
from arcade_app.games.memory_match.game import MemoryMatchGame
from arcade_app.games.minesweeper.game import MinesweeperGame
from arcade_app.games.platformer.game import PlatformerGame
from arcade_app.games.pong.game import PongGame
from arcade_app.games.reaction_timer.game import ReactionTimerGame
from arcade_app.games.simon_says.game import SimonSaysGame
from arcade_app.games.snake.game import SnakeGame
from arcade_app.games.space_invaders.game import SpaceInvadersGame
from arcade_app.games.sudoku.game import SudokuGame
from arcade_app.games.tetris.game import TetrisGame
from arcade_app.games.tic_tac_toe.game import TicTacToeGame
from arcade_app.games.time_attack_challenge.game import TimeAttackChallengeGame
from arcade_app.games.top_down_shooter.game import TopDownShooterGame
from arcade_app.games.whac_a_mole.game import WhacAMoleGame
from arcade_app.scenes.placeholder_game_scene import PlaceholderGameScene


GAME_REGISTRY = sorted(
    [
        {
            "id": "advanced_target_trainer",
            "title": "Advanced Target Trainer",
            "description": "Track multiple pop-up targets, build combos, and keep accuracy high under pressure.",
            "category": "Skill",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": AdvancedTargetTrainerGame,
        },
        {
            "id": "aim_trainer",
            "title": "Aim Trainer",
            "description": "Click targets quickly, build accuracy, and maximise your reaction-speed score.",
            "category": "Skill",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": AimTrainerGame,
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
            "id": "battleships",
            "title": "Battleships",
            "description": "Place your fleet and hunt down the enemy ships.",
            "category": "Strategy",
            "modes": ["PvP", "PvC"],
            "implemented": True,
            "scene_class": BattleshipsGame,
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
            "id": "connect4",
            "title": "Connect 4",
            "description": "Drop discs and connect four before your opponent does.",
            "category": "Strategy",
            "modes": ["PvP", "PvC"],
            "implemented": True,
            "scene_class": Connect4Game,
        },
        {
            "id": "dodge_falling_blocks",
            "title": "Dodge the Falling Blocks",
            "description": "Slide left and right, dodge dense falling hazards, and survive as the pace ramps up.",
            "category": "Arcade",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": DodgeFallingBlocksGame,
        },
        {
            "id": "endless_runner",
            "title": "Endless Runner",
            "description": "Sprint forward, jump and duck through hazards, and survive a faster and faster run.",
            "category": "Arcade",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": EndlessRunnerGame,
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
            "id": "frogger_clone",
            "title": "Frogger Clone",
            "description": "Cross busy roads and dangerous rivers to reach every safe home slot.",
            "category": "Arcade",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": FroggerCloneGame,
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
            "id": "hangman",
            "title": "Hangman",
            "description": "Guess the hidden word from themed categories before you run out of lives.",
            "category": "Word",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": HangmanGame,
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
            "id": "memory_match",
            "title": "Memory Match",
            "description": "Flip cards, match pairs, and test your memory across difficulties.",
            "category": "Puzzle",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": MemoryMatchGame,
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
            "id": "platformer",
            "title": "Platformer",
            "description": "Jump across platforms, collect every coin, and reach the exit.",
            "category": "Action",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": PlatformerGame,
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
            "id": "reaction_timer",
            "title": "Reaction Timer",
            "description": "Wait for the signal, react instantly, and avoid false starts across timed rounds.",
            "category": "Skill",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": ReactionTimerGame,
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
            "id": "snake",
            "title": "Snake",
            "description": "Grow longer, avoid collisions, and chase a higher score.",
            "category": "Arcade",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": SnakeGame,
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
            "id": "sudoku",
            "title": "Sudoku",
            "description": "Solve a fresh puzzle each run with notes and mistake tracking.",
            "category": "Puzzle",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": SudokuGame,
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
            "id": "tic_tac_toe",
            "title": "Tic Tac Toe",
            "description": "Classic 3x3 strategy game with PvP and PvC play.",
            "category": "Strategy",
            "modes": ["PvP", "PvC"],
            "implemented": True,
            "scene_class": TicTacToeGame,
        },
        {
            "id": "time_attack_challenge",
            "title": "Time Attack Challenge",
            "description": "Race the clock, chain pickups together, and dodge hazards for a high-score rush.",
            "category": "Arcade",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": TimeAttackChallengeGame,
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
            "id": "whac_a_mole",
            "title": "Whac-A-Mole",
            "description": "React quickly and hit moles before time runs out.",
            "category": "Arcade",
            "modes": ["Solo"],
            "implemented": True,
            "scene_class": WhacAMoleGame,
        },
    ],
    key=lambda game: str(game["title"]).lower(),
)


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