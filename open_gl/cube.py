import numpy as np
from scipy.spatial.transform.rotation import Rotation

from utils import Color


class Cube:
    SURFACES = {
        "U": (2, 3, 7, 6),
        "D": (4, 5, 1, 0),
        "L": (0, 1, 3, 2),
        "R": (6, 7, 5, 4),
        "F": (1, 5, 7, 3),
        "B": (4, 0, 2, 6)
    }
    EDGES = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6),
             (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)]

    COLORS = {"U": Color.WHITE, "D": Color.YELLOW,
              "L": Color.BLUE, "R": Color.GREEN,
              "F": Color.ORANGE, "B": Color.RED}

    base_verticies = np.array([(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]) / 2

    def __init__(self, initial_position=None, initial_rotation=None, colors=None):
        self.position = np.zeros(3) if initial_position is None else initial_position
        self.rotation: Rotation = Rotation.identity() if initial_rotation is None else initial_rotation
        self.colors = self.COLORS if colors is None else colors
        self.update_verticies()

    def update_verticies(self):
        self.verticies = self.rotation.apply(self.base_verticies) + self.position

    def rotate(self, rot):
        self.rotation = rot * self.rotation
        self.position = rot.apply(self.position)
        self.update_verticies()


