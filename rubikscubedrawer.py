from dataclasses import dataclass
from functools import cached_property

import numpy as np
import pygame
from OpenGL.GLU import *
from pygame.locals import *
from scipy.spatial.distance import cdist
from scipy.spatial.transform import Rotation

from cube import Cube
from utils import Color, Queue


@dataclass
class FaceRotationAnimation:
    DEG_PER_SEC = 100
    face: str
    start: int
    current_angle: float
    target_angle: float
    reverse: bool


class RubiksCube:
    offset = 1.1

    # TODO compute cube current state
    # TODO start cube from given state

    def __init__(self):
        colors = [
            {"U": Color.WHITE if y == 1 else Color.HIDDEN,
             "D": Color.YELLOW if y == -1 else Color.HIDDEN,
             "L": Color.BLUE if x == -1 else Color.HIDDEN,
             "R": Color.GREEN if x == 1 else Color.HIDDEN,
             "F": Color.ORANGE if z == 1 else Color.HIDDEN,
             "B": Color.RED if z == -1 else Color.HIDDEN}
            for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)
        ]
        colors.pop(13)
        self.cubes = [
            Cube(pos, cols) for i, (pos, cols) in enumerate(zip(self.default_positions, colors))
        ]

        self.faces = self.default_faces

        self._animation: Queue = Queue()  # Stores animations to move faces

    @cached_property
    def default_positions(self):
        default_positions = [
            [self.offset * x, self.offset * y, self.offset * z]
            for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)
        ]
        default_positions.pop(13)
        return default_positions

    @cached_property
    def default_faces(self):
        center = 13
        up, right, front = 3, 9, 1
        base = (up, right, front)
        deltas = {"U": up, "D": -up, "R": right, "L": -right, "F": front, "B": -front}
        faces = {}
        moves = (-1, 0, 1)
        for face, delta in deltas.items():
            c = center + delta
            [d1, d2] = [d for d in base if d != abs(delta)]
            cubes = [c + a * d1 + b * d2 for a in moves for b in moves]
            cubes = [c if c < 14 else c - 1 for c in cubes]
            faces[face] = cubes
        return faces

    def compute_faces(self):
        # /!\ Assumes the cube is never moved / rotated / scaled
        # Find permutation from start
        positions = np.array([c.position for c in self.cubes])
        _, permutation = np.where(cdist(positions, self.default_positions).T < self.offset / 10)
        # Apply permutation to state
        self.faces = {f: permutation[cube_ids] for f, cube_ids in self.default_faces.items()}

    def get_normal(self, face):
        x, y, z = np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])
        if face == "F":
            return -z
        elif face == "B":
            return z
        elif face == "L":
            return x
        elif face == "R":
            return -x
        elif face == "U":
            return y
        elif face == "D":
            return -y
        else:
            raise ArgumentError(f"Wrong face value: {face}")

    def draw(self):
        for cube in self.cubes:
            cube.draw()

    def animate(self, dt):
        # Needs to be called for each frame in case there are animations to run
        if self._animation.empty():
            return
        anim = self._animation.peek()  # Get current face animation
        speed_deg = dt * anim.DEG_PER_SEC / 1000
        if anim.current_angle >= anim.target_angle:
            self.finish_animation()
            return

        speed_rad = np.radians(speed_deg)
        delta = speed_rad if not anim.reverse else -speed_rad
        rot_vec = delta * self.get_normal(anim.face)
        rot = Rotation.from_rotvec(rot_vec)
        for cube_id in self.faces[anim.face]:
            cube = self.cubes[cube_id]
            cube.rotate(rot)
        anim.current_angle += speed_deg

    def finish_animation(self):
        # Round cubes position
        positions = np.array([c.position for c in self.cubes])
        round_positions = np.round(positions / self.offset) * self.offset
        rotations = np.array([c.rotation.as_euler("xyz") for c in self.cubes])
        round_rotations = np.round(rotations / np.pi * 2) * np.pi / 2
        for c, pos, rot in zip(self.cubes, round_positions, round_rotations):
            c.position = pos
            c.rotation = Rotation.from_euler("xyz", rot)

        self.compute_faces()
        self._animation.pop()

    def move_face(self, face, angle=90, reverse=False):
        self._animation.put(
            FaceRotationAnimation(face, pygame.time.get_ticks(), 0, angle, reverse)
        )

    def shuffle(self):
        # Shuffles only one way (no U')...
        len = 30
        # moves = np.random.choice(list(self.faces.keys()), len)
        moves = ['F', 'R']
        print(moves)
        cubes = np.arange(26)
        rots_cube = {i: Rotation.identity() for i in cubes}
        for face in moves:
            rot = Rotation.from_rotvec(np.pi / 2 * self.get_normal(face))
            cubes_ids = np.array(self.default_faces[face])  # 9 cubes in face
            cubes_to_rotate = cubes[cubes_ids]
            for c in cubes_to_rotate:
                rots_cube[c] = rot * rots_cube[c]
            cubes[cubes_ids] = cubes[cubes_ids[[2, 5, 8, 1, 4, 7, 0, 3, 6]]]

        # Apply combinaison of moves
        for cube_id, rot in rots_cube.items():
            self.cubes[cube_id].rotate(rot)
        # Recompute state
        self.compute_faces()

