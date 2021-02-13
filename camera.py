import numpy as np
from OpenGL.GL import *
from scipy.spatial.transform.rotation import Rotation

from ui.events_hub import EventsHub, Event


class Camera:
    SLOW_ROT_SPEED = 0.02

    def __init__(self, event_hub: EventsHub):
        self.camera_rot = Rotation.identity()
        self.rot_delta = Rotation.from_rotvec([0, self.SLOW_ROT_SPEED, 0])
        self.event_hub = event_hub
        self._add_listeners()

    def reset_view(self):
        self.camera_rot = Rotation.identity()

    def apply_view(self):
        # Applies absolute camera position (not hyper efficient)
        self.camera_rot = self.rot_delta * self.camera_rot
        glPopMatrix()
        glPushMatrix()
        rotvec = self.camera_rot.as_rotvec()
        glRotate(np.degrees(np.linalg.norm(rotvec)), *rotvec)

    def rotate(self, direction, angle):
        # rotate view around axis
        if direction in ["RIGHT", "LEFT"]:
            sign = 1 if direction == "RIGHT" else -1
            rot = Rotation.from_rotvec([0, sign * angle, 0])
            self.camera_rot = rot * self.camera_rot
        else:
            sign = 1 if direction == "UP" else -1
            rot = Rotation.from_rotvec([sign * angle, 0, 0])
            self.camera_rot = rot * self.camera_rot

    def toggle_cube_rot(self):
        if np.linalg.norm(self.rot_delta.as_rotvec()) < 0.01:
            self.rot_delta = Rotation.from_rotvec([0, self.SLOW_ROT_SPEED, 0])
        else:
            self.rot_delta = Rotation.identity()

    def _add_listeners(self):
        self.event_hub.add_callback(Event.CAMERA_MOVE,
                                    lambda event: self.rotate(event.direction, event.angle))
        self.event_hub.add_callback(Event.CAMERA_RESET,
                                    lambda ev: self.reset_view())
        self.event_hub.add_callback(Event.CAMERA_TOGGLE_ROT,
                                    lambda ev: self.toggle_cube_rot())
        self.event_hub.add_callback(Event.NEWFRAME,
                                    lambda ev: self.apply_view())
