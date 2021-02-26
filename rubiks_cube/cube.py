import kociemba
import numpy as np

from rubiks_cube.constants import FACE_ORDER
from rubiks_cube.core import get_normal, get_face_for_normal, get_color_from_state_str, get_rot_from_basis
from rubiks_cube.cubic_mathematics import CubicRotation


class Cube:
    """This class represents a simple 3D Cube, which you can rotate but only
    with transforms possible on a rubiks cube.
    A cube is identified by its colors, a list of face color or None if no color.
    """
    def __init__(self, initial_rotation=None, colors=None, id=None):
        self.rotation: CubicRotation = CubicRotation() if initial_rotation is None else initial_rotation
        self.colors = colors  # Boolean array identifying the colors shown
        self.id = -1 if id is None else id

    def rotate(self, rot):
        """Apply rotation to cube position and orientation."""
        self.rotation = rot * self.rotation

    def get_color_on_face(self, face):
        normal = get_normal(face)
        from_normal = self.rotation.inv().apply(normal)
        return get_face_for_normal(from_normal)

    def __eq__(self, other):
        return self.rotation == other.rotation and self.colors == other.colors and self.id == other.id

    def __str__(self):
        return f"Cube {self.id}: {self.colors=} - {self.rotation}"


def generate_cubes():
    cubes = []
    id = 0
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            for z in (-1, 0, 1):
                if x == y == z == 0:
                    continue
                colors = [
                    y == 1,   # U
                    x == 1,   # R
                    z == 1,   # F
                    y == -1,  # D
                    x == -1,  # L
                    z == -1   # B
                ]
                cube = Cube(colors=colors, id=id)
                cubes.append(cube)
                id += 1
    return np.array(cubes)


def generate_cubes_from_state_str(state_str, check=False):
    if check:
        try:
            kociemba.solve(state_str)
        except ValueError as e:
            raise ValueError(f"Invalid state string {state_str}")

    base = np.eye(3)
    cubes = [None] * 26
    i = 0
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            for z in (-1, 0, 1):
                if x == y == z == 0:  # Skip center cube
                    continue
                pos = np.array([x, y, z])

                colors = [False] * 6
                basis = [None] * 3
                for axis in np.where(pos != 0)[0]:
                    color = get_color_from_state_str(state_str, pos, pos[axis] * base[axis])
                    norm = get_normal(color)
                    basis[axis] = norm * pos[axis]
                    colors[FACE_ORDER.index(color)] = True

                rot = get_rot_from_basis(basis)
                original_pos = rot.apply(pos)
                ox, oy, oz = original_pos
                id = 9 * (ox + 1) + 3 * (oy + 1) + (oz + 1)
                index = 9 * (x + 1) + 3 * (y + 1) + (z + 1)
                if index > 13:
                    index = index - 1
                if id > 13:
                    id = id - 1
                cube = Cube(initial_rotation=rot.inv(), colors=colors, id=id)
                cubes[index] = cube
                i += 1
    return np.array(cubes)

