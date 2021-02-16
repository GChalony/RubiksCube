from dataclasses import dataclass

import numpy as np
import pygame
from OpenGL.GL import *
from pygame.locals import *
from scipy.spatial.transform import Rotation

from rubikscube.core import get_normal
from rubikscube.rubikscube import RubiksCube
from ui.events_hub import Event, EventsHub
from utils import Color, Queue


@dataclass
class FaceRotationAnimation:
    DEG_PER_SEC = 100
    face: str
    start: int
    current_angle: float
    target_angle: float
    reverse: bool
    cubes: list = None


class RubiksCubeDrawer:
    def __init__(self, event_hub: EventsHub):
        self.state = RubiksCube()
        self._animation: Queue = Queue()  # Stores animations to move faces
        self.event_hub = event_hub
        self._add_listeners()

    def _add_listeners(self):
        self.event_hub.add_callback(Event.CUBE_MOVE_FACE,
                                    lambda event: self.move_face(event.face, 90, event.reverse))
        self.event_hub.add_callback(Event.NEWFRAME,
                                    lambda event: self._animate(event.dt))

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
            color = cube.colors[face]
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

    def _animate(self, dt):
        # Needs to be called for each frame in case there are animations to run
        if self._animation.empty():
            return
        anim = self._animation.peek()  # Get current face animation
        if anim.cubes is None:  # If first frame
            anim.cubes = self.state.get_cubes_on_face(anim.face)

        speed_deg = dt * anim.DEG_PER_SEC / 1000
        if anim.current_angle >= anim.target_angle - speed_deg:
            self._finish_animation()
            return

        speed_rad = np.radians(speed_deg)
        delta = -speed_rad if not anim.reverse else speed_rad
        rot_vec = delta * get_normal(anim.face)
        rot = Rotation.from_rotvec(rot_vec)
        for cube in anim.cubes:
            cube.rotate(rot)
        anim.current_angle += speed_deg

    def _finish_animation(self):
        # Round cubes position
        positions = np.array([c.position for c in self.state.cubes])
        round_positions = np.round(positions / self.state.offset) * self.state.offset
        rotations = np.array([c.rotation.as_euler("xyz") for c in self.state.cubes])
        round_rotations = np.round(rotations / np.pi * 2) * np.pi / 2
        for c, pos, rot in zip(self.state.cubes, round_positions, round_rotations):
            c.position = pos
            c.rotation = Rotation.from_euler("xyz", rot)

        self._animation.pop()
        # TODO do in different thread
        self.event_hub.raise_event(Event(origin=Event.APPLICATION, type=Event.ANIMATIONFINISHED,
                                         state_str=self.state.compute_state_string()))

    def move_face(self, face, angle=90, reverse=False):
        """Start move face animation."""
        self._animation.put(
            FaceRotationAnimation(face=face, start=pygame.time.get_ticks(),
                                  current_angle=0, target_angle=angle, reverse=reverse)
        )
