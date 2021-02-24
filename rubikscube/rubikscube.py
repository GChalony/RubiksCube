import kociemba
import numpy as np
from colorama import Back
from scipy.spatial.transform.rotation import Rotation

from rubikscube.core import generate_cubes, get_normal, get_face_for_normal, \
    generate_cubes_from_state_str, FACE_ORDER, ALL_MOVES, get_cube_ids_on_face, state_str_to_state_description


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
    SOLVED_STR = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    TERM_COLORS = {"U": "\033[48;5;15m", "R": Back.GREEN, "F": "\033[48;5;202m",
                   "D": "\033[48;5;11m", "L": Back.BLUE, "B": "\033[48;5;196m"}

    def __init__(self, state=None):
        self.cubes = generate_cubes()
        self._compute_state_string()
        self.state_string = state if state is not None else self.SOLVED_STR
        self.history_moves = []

    def __repr__(self):
        return f"<Cube: {self.state_string}>"

    def __str__(self):
        return state_str_to_state_description(self.state_string)

    def pprint(self):
        [u, r, f, d, l, b] = [self.state_string[9 * i: 9 * (i + 1)] for i in range(6)]
        ordered = (*u, *l[:3], *f[:3], *r[:3], *b[:3],
                   *l[3:6], *f[3:6], *r[3:6], *b[3:6],
                   *l[6:9], *f[6:9], *r[6:9], *b[6:9], *d)
        colors = [self.TERM_COLORS[f]+"   \033[0m" for f in ordered]
        pattern = """\n         {}{}{}
         {}{}{}
         {}{}{}
{}{}{}{}{}{}{}{}{}{}{}{}
{}{}{}{}{}{}{}{}{}{}{}{}
{}{}{}{}{}{}{}{}{}{}{}{}
         {}{}{}
         {}{}{}
         {}{}{}"""
        print(pattern.format(*colors))

    def get_cubes_on_face(self, face):
        return self.cubes[get_cube_ids_on_face(self.cubes, face)]

    def _compute_state_string(self):
        state_str = ""
        for face in FACE_ORDER:
            cubes = self.get_cubes_on_face(face)
            normal = get_normal(face)
            for c in cubes:
                vect = c.rotation.inv().apply(normal)
                letter = get_face_for_normal(vect)
                state_str += letter
        self.state_string = state_str

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
        self._compute_state_string()

    def shuffle(self, n=30):
        possible_moves = ALL_MOVES
        moves = np.random.choice(possible_moves, n)
        print("Shuffling: ", " ".join(moves))
        for move in moves:
            self.move(move)
        return moves

    def is_solved(self):
        return self.state_string == RubiksCube.SOLVED_STR

    def load_state(self, state_str):
        self.cubes = generate_cubes_from_state_str(state_str)
        self.state_string = state_str
        self.history_moves = []


if __name__ == '__main__':
    cube = RubiksCube()
    cube.shuffle(30)
    state = cube.state_string
    print("State", state)
    solution = kociemba.solve(state)
    print("Applying solution", solution)
    for move in solution.split(" "):
        cube.move(move)
    print(cube.state_string)
    print("Solved!" if cube.is_solved() else "Not solved...")
