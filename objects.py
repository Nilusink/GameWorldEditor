from dataclasses import dataclass


@dataclass(frozen=False)
class Floor:
    color: tuple[float, float, float, float]
    position: tuple[float, float]
    size: tuple[float, float]


@dataclass(frozen=False)
class Destroyable:
    position: tuple[float, float]
    hp: float
    image_path: str = ""
    name: str = ""


@dataclass(frozen=False)
class Turret:
    position: tuple[float, float]
    weapon: str
    image_path: str = "./images/characters/turret/turret.png"
