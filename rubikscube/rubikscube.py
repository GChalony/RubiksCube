import kociemba
import numpy as np
from scipy.spatial.transform.rotation import Rotation

from rubikscube.core import generate_cubes, get_normal, get_face_for_normal, get_cubes_on_face, generate_cubes_from_state_str


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
        return get_cubes_on_face(self.cubes, face, self.offset)

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
        return state == RubiksCube.SOLVED_STR

    def load_state(self, state_str):
        self.cubes = generate_cubes_from_state_str(state_str, self.offset)
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
