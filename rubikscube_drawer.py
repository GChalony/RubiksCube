from dataclasses import dataclass

import numpy as np
import pygame
from OpenGL.GL import *
from pygame.locals import *
from scipy.spatial.transform import Rotation

from rubikscube import RubiksCube
from utils import Color, Queue


@dataclass
class FaceRotationAnimation:
    DEG_PER_SEC = 100
    face: str
    cubes: list
    start: int
    current_angle: float
    target_angle: float
    reverse: bool


class RubiksCubeDrawer:
    def __init__(self):
        self.state = RubiksCube()
        self._animation: Queue = Queue()  # Stores animations to move faces

    @staticmethod
    def _draw_square(corners, color):
        """Draw a square using """
        normal = np.cross(corners[3] - corners[0], corners[1] - corners[0])
        normal = normal / np.linalg.norm(normal)
        glNormal3fv(tuple(normal))
        glColor3fv(color)
        glBegin(GL_QUADS)
        for vertex in corners:
            glVertex3fv(tuple(vertex))
        glEnd()
        glColor3fv(Color.WHITE)

    @staticmethod
    def _draw_cube(cube):
        for face in cube.SURFACES.keys():
            surface = np.array(cube.SURFACES[face])
            color = cube.colors[face]  # TODO extract color info from cube
            corners = cube.verticies[surface]
            RubiksCubeDrawer._draw_square(corners, color)

        glBegin(GL_LINES)
        glColor3fv(Color.BLACK)
        for edge in cube.EDGES:
            for v in edge:
                vertex = cube.verticies[v]
                glVertex3fv(tuple(vertex))
        glEnd()

    def draw(self):
        for cube in self.state.cubes:
            RubiksCubeDrawer._draw_cube(cube)

    def animate(self, dt):
        # Needs to be called for each frame in case there are animations to run
        if self._animation.empty():
            return
        anim = self._animation.peek()  # Get current face animation
        speed_deg = dt * anim.DEG_PER_SEC / 1000
        if anim.current_angle >= anim.target_angle - speed_deg:
            self.finish_animation()
            return

        speed_rad = np.radians(speed_deg)
        delta = -speed_rad if not anim.reverse else speed_rad
        rot_vec = delta * self.state.get_normal(anim.face)
        rot = Rotation.from_rotvec(rot_vec)
        for cube in anim.cubes:
            cube.rotate(rot)
        anim.current_angle += speed_deg

    def finish_animation(self):
        # Round cubes position
        positions = np.array([c.position for c in self.state.cubes])
        round_positions = np.round(positions / self.state.offset) * self.state.offset
        rotations = np.array([c.rotation.as_euler("xyz") for c in self.state.cubes])
        round_rotations = np.round(rotations / np.pi * 2) * np.pi / 2
        for c, pos, rot in zip(self.state.cubes, round_positions, round_rotations):
            c.position = pos
            c.rotation = Rotation.from_euler("xyz", rot)

        self._animation.pop()

    def move_face(self, face, angle=90, reverse=False):
        self._animation.put(
            FaceRotationAnimation(face=face, cubes=self.state.get_cubes_on_face(face),
                                  start=pygame.time.get_ticks(), current_angle=0,
                                  target_angle=angle, reverse=reverse)
        )
