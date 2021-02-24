import numpy as np
from scipy.spatial.transform.rotation import Rotation


class Cube:
    """This class represents a simple 3D Cube, which you can rotate and translate but only
    with transforms possible on a rubiks cube.
    A cube is identified by its colors, a list of face color or None if no color.
    """
    def __init__(self, initial_position=None, initial_rotation=None, colors=None):
        self.position = np.zeros(3) if initial_position is None else initial_position
        self.rotation: Rotation = Rotation.identity() if initial_rotation is None else initial_rotation
        self.colors = colors

    def rotate(self, rot):
        """Apply rotation to cube position and orientation."""
        # TODO ignore UserWarning: Gimbal lock
        self.rotation = rot * self.rotation
        self.rotation = Rotation.from_euler("xyz",
            np.round(self.rotation.as_euler("xyz") / np.pi * 2) * np.pi / 2
        )
        self.position = np.round(rot.apply(self.position))