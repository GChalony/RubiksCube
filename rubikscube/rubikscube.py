import kociemba
import numpy as np
from scipy.spatial.distance import cdist
from scipy.spatial.transform.rotation import Rotation

from rubikscube.core import generate_cubes, get_normal, get_up_on_face, get_face_for_normal


class RubiksCube:
    """This class is meant to represent a rubikscube state,
    switching between different representations and access some primitives.
    The different representations are:
     - list of colors:  UUUUUULLLURRURRURRFFFFFFFFFRRRDDDDDDLLDLLDLLDBBBBBBBBB
     - list of 26 3D positions and rotations (one per cube) - NOT ORDERED
     - history of moves: FL'RU'...
     One important primitive:
     - List of cubes on one face (needed for animation)
     - Cubes permutation
    """
    SOLVED_STR="UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

    def __init__(self, state=None):
        self.offset = 1.1
        self.cubes = generate_cubes(self.offset)
        self.state_string = state if state is not None else "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
        self.history_moves = []

    def get_cubes_on_face(self, face):
        """Returns the 9 cubes on given face, ordered from top_left to bottom right."""
        normal = get_normal(face)
        up = get_up_on_face(face)
        right = np.cross(up, normal)
        positions = [self.offset * (normal + x * right + y * up)
                     for y in (1, 0, -1) for x in (-1, 0, 1)]
        current_positions = [c.position for c in self.cubes]
        dist_matrix = cdist(current_positions, positions)
        cubes_ids = np.where((dist_matrix < 0.1).T)[1]
        cubes = self.cubes[cubes_ids]
        return cubes

    def compute_state_string(self):
        state_str = ""
        for face in ["U", "R", "F", "D", "L", "B"]:
            cubes = self.get_cubes_on_face(face)
            normal = get_normal(face)
            for c in cubes:
                vect = c.rotation.inv().apply(normal)
                letter = get_face_for_normal(vect)
                state_str += letter
        return state_str

    def move(self, f):
        self.history_moves.append(f)
        face = f[0]
        reverse = "'" in f
        double = "2" in f
        cubes = self.get_cubes_on_face(face)
        normal = get_normal(face)
        sign = 1 if reverse else -1
        rot = Rotation.from_rotvec((1 + double) * sign * np.pi / 2 * normal)
        for cube in cubes:
            cube.rotate(rot)

    def shuffle(self, n=30):
        possible_moves = ["F", "F'", "R", "R'", "L", "L'", "U", "U'", "D", "D'", "B", "B'"]
        moves = np.random.choice(possible_moves, n)
        print("Shuffling: ", " ".join(moves))
        for move in moves:
            self.move(move)

    def is_solved(self):
        state = self.compute_state_string()
        return state == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

    def load_state(self, state_str):
        # Check valid
        try:
            kociemba.solve(state_str)
        except ValueError as e:
            raise ValueError(f"Invalid state string {state_str}")
        # Need to change cubes colors, as if gluing stickers
        for i, face in enumerate(["U", "R", "F", "D", "L", "B"]):
            cubes = self.get_cubes_on_face(face)
            normal = get_normal(face)
            for j, cube in enumerate(cubes):
                vect = cube.rotation.inv().apply(normal)
                f = get_face_for_normal(vect)
                # TODO find rotation for cube then apply colors

        self.state_string = state_str
        self.history_moves = []


if __name__ == '__main__':
    cube = RubiksCube()
    cube.shuffle(30)
    state = cube.compute_state_string()
    print("State", state)
    solution = kociemba.solve(state)
    print("Applying solution", solution)
    for move in solution.split(" "):
        cube.move(move)
    print(cube.compute_state_string())
    print("Solved!" if cube.is_solved() else "Not solved...")
