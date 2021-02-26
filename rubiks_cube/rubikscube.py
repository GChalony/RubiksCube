from typing import List

import kociemba
import numpy as np
from colorama import Back

from rubiks_cube.constants import ALL_MOVES, FACE_ORDER
from rubiks_cube.core import get_cube_ids_on_face, state_str_to_state_description, get_rot, get_permutation
from rubiks_cube.cube import generate_cubes, generate_cubes_from_state_str, Cube


class RubiksCube:
    """This class is meant to represent a rubiks_cube state,
    switching between different representations and access some primitives.
    The different representations are:
     - list of colors:  UUUUUULLLURRURRURRFFFFFFFFFRRRDDDDDDLLDLLDLLDBBBBBBBBB
     - list of 26 3D positions and rotations (one per cube) - ORDERED
     - history of moves: FL'RU'...
     Some important primitive:
     - List of cubes on one face (needed for animation)
     - Cubes permutation
    """
    SOLVED_STR = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    TERM_COLORS = {"U": "\033[48;5;15m", "R": Back.GREEN, "F": "\033[48;5;202m",
                   "D": "\033[48;5;11m", "L": Back.BLUE, "B": "\033[48;5;196m"}
    ORDERED_CUBES_POSITIONS = [np.array([x, y, z])
                               for x in (-1, 0, 1)
                               for y in (-1, 0, 1)
                               for z in (-1, 0, 1)
                               if not (x == y == z == 0)]

    def __init__(self, state=None):
        self.cubes: List[Cube] = generate_cubes()
        # self._compute_state_string()
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

    def get_cubes_on_face(self, face) -> List[Cube]:
        return self.cubes[get_cube_ids_on_face(face)]

    def _compute_state_string(self):
        state_str = ""
        # TODO iterate over cubes rather than faces
        for face in FACE_ORDER:
            cubes = self.get_cubes_on_face(face)
            for c in cubes:
                letter = c.get_color_on_face(face)
                state_str += letter
        self.state_string = state_str

    def move(self, f, lazy=False):
        self.history_moves.append(f)
        face = f[0]
        reverse = "'" in f
        double = "2" in f
        # Apply rotation to all cubes
        rot = get_rot(face, reverse, double)
        for c in self.get_cubes_on_face(face):
            c.rotate(rot)
        # Permute cubes order
        permutation = get_permutation(face, reverse, double)
        self.cubes = self.cubes[permutation]
        if not lazy:
            self._compute_state_string()

    def shuffle(self, n=30):
        possible_moves = ALL_MOVES
        moves = np.random.choice(possible_moves, n)
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
