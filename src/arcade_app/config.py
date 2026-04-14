from dataclasses import dataclass

from arcade_app.constants import BASE_HEIGHT, BASE_WIDTH, FPS


@dataclass(slots=True)
class AppConfig:
    width: int = BASE_WIDTH
    height: int = BASE_HEIGHT
    fps: int = FPS
    fullscreen: bool = False
    sound_enabled: bool = True
    music_enabled: bool = True
