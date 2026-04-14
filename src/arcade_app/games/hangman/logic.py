from __future__ import annotations

import random

from arcade_app.games.hangman.data import WORD_BANK


class HangmanLogic:
    MAX_WRONG_GUESSES = 6

    def __init__(self) -> None:
        self.category = "Animals"
        self.reset(self.category)

    def reset(self, category: str | None = None) -> None:
        if category is not None:
            self.category = category

        words = WORD_BANK[self.category]
        self.word = random.choice(words)
        self.guessed_letters: set[str] = set()
        self.wrong_letters: list[str] = []
        self.wrong_guesses = 0
        self.is_won = False
        self.is_lost = False

    def guess_letter(self, letter: str) -> bool:
        if self.is_won or self.is_lost:
            return False

        if not letter or len(letter) != 1 or not letter.isalpha():
            return False

        letter = letter.upper()

        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False

        if letter in self.word:
            self.guessed_letters.add(letter)
            self.check_win()
            return True

        self.wrong_letters.append(letter)
        self.wrong_guesses += 1

        if self.wrong_guesses >= self.MAX_WRONG_GUESSES:
            self.is_lost = True

        return True

    def check_win(self) -> None:
        unique_letters = {ch for ch in self.word if ch.isalpha()}
        if unique_letters.issubset(self.guessed_letters):
            self.is_won = True

    def get_display_word(self) -> str:
        chars: list[str] = []
        for ch in self.word:
            if ch == " ":
                chars.append(" ")
            elif ch in self.guessed_letters:
                chars.append(ch)
            else:
                chars.append("_")
        return " ".join(chars)

    def get_status_text(self) -> str:
        if self.is_won:
            return "You won!"
        if self.is_lost:
            return f"You lost! Word: {self.word}"
        return "Guess a letter"