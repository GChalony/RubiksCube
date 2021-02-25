from dataclasses import dataclass

import numpy as np
import pygame
from pygame.locals import *
from scipy.spatial.transform import Rotation

from open_gl.cube import Cube
from rubiks_cube.core import get_normal, get_cube_ids_on_face
from rubiks_cube.constants import FACE_ORDER
from rubiks_cube.rubikscube import RubiksCube
from events_hub import Event, EventsHub
from utils import Color, Queue


@dataclass
class FaceRotationAnimation:
    DEG_PER_SEC = 100
    move: str
    face: str
    start: int
    current_angle: float
    target_angle: float
    reverse: bool
    cubes: list = None


class RubiksCubeDrawer:
    COLORS = {
        "U": Color.WHITE,
        "D": Color.YELLOW,
        "L": Color.BLUE,
        "R": Color.GREEN,
        "F": Color.ORANGE,
        "B": Color.RED
    }
    offset = 1.02

    def __init__(self, event_hub: EventsHub):
        self.state = RubiksCube()
        self._generate_cubes(self.state.cubes)
        self._animation: Queue = Queue()  # Stores animations to move faces
        self.event_hub = event_hub

        self._add_listeners()

    def _generate_cubes(self, state_cubes):
        """Generate OpenGL cubes from state.cubes.
        These two lists should remain synced at all times... or should they?
        """
        cubes = []
        for c in state_cubes:
            x, y, z = c.position
            colors = {FACE_ORDER[i]: self.COLORS[v] if v is not None else Color.HIDDEN
                      for i, v in enumerate(c.colors)}
            cubes.append(Cube(self.offset * c.position, c.rotation, colors=colors))
        self.cubes = np.array(cubes)

    def _add_listeners(self):
        self.event_hub.add_callback(Event.CUBE_MOVE_FACE,
                                    lambda event: self.move(event.face))
        self.event_hub.add_callback(Event.NEWFRAME,
                                    lambda event: self._animate(event.dt))
        self.event_hub.add_callback(Event.CUBE_SHUFFLE,
                                    lambda event: self.shuffle())

    def draw(self):
        for cube in self.cubes:
            cube.draw()

    def _animate(self, dt):
        # Needs to be called for each frame to run animations
        if self._animation.empty():
            return
        anim = self._animation.peek()  # Get current face animation
        if anim.current_angle == 0:  # If first frame
            cube_ids = get_cube_ids_on_face(self.state.cubes, anim.face)
            anim.cubes = self.cubes[cube_ids]
            self.state.move(anim.move)

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
        # Resync state.cubes and self.cubes
        for c, model in zip(self.cubes, self.state.cubes):
            c.position = model.position * self.offset
            c.rotation = model.rotation
            c.update_verticies()

        self._animation.pop()
        self._raise_state_changed()

    def _raise_state_changed(self):
        self.event_hub.raise_event(Event(origin=Event.APPLICATION, type=Event.CUBE_STATE_CHANGED,
                                         state_str=self.state.state_string,
                                         is_solved=self.state.is_solved()))

    def move(self, move):
        """Start move face animation."""
        face = move[0]
        reverse = "'" in move
        angle = 90 * (1 + ("2" in move))
        self._animation.put(
            FaceRotationAnimation(move=move, face=face, start=pygame.time.get_ticks(),
                                  current_angle=0, target_angle=angle, reverse=reverse
                                  )
        )

    def load_state(self, state_str):
        self._animation.remove_all()
        self.state.load_state(state_str)
        self._generate_cubes(self.state.cubes)
        self._raise_state_changed()

    def shuffle(self):
        self._animation.remove_all()
        self.state.shuffle()
        self._generate_cubes(self.state.cubes)
        self._raise_state_changed()

