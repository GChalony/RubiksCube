import kociemba
import numpy as np
from scipy.spatial.distance import cdist
from scipy.spatial.transform.rotation import Rotation

from cube import Cube, ArgumentError
from utils import Color

# TODO separate cubes face colors and actual colors to drawing part
color_for_face = {"U": Color.WHITE, "D": Color.YELLOW,
          "L": Color.BLUE, "R": Color.GREEN,
          "F": Color.ORANGE, "B": Color.RED}


class RubiksCubeState:
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

    def __init__(self, state=None):
        self.offset = 1.1
        self.cubes = self.generate_cubes()
        self.state_string = state if state is not None else "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
        self.history_moves = []

    def generate_cubes(self):
        cubes = []
        for x in (-1, 0, 1):
            for y in (-1, 0, 1):
                for z in (-1, 0, 1):
                    if x == y == z == 0:
                        continue
                    colors = {"U": Color.WHITE if y == 1 else Color.HIDDEN,
                              "D": Color.YELLOW if y == -1 else Color.HIDDEN,
                              "L": Color.BLUE if x == -1 else Color.HIDDEN,
                              "R": Color.GREEN if x == 1 else Color.HIDDEN,
                              "F": Color.ORANGE if z == 1 else Color.HIDDEN,
                              "B": Color.RED if z == -1 else Color.HIDDEN
                              }
                    pos = [self.offset * x, self.offset * y, self.offset * z]
                    cube = Cube(pos, colors)
                    cubes.append(cube)
        return np.array(cubes)

    @staticmethod
    def get_normal(face):
        x, y, z = np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])
        if face == "F":
            return -z
        elif face == "B":
            return z
        elif face == "L":
            return x
        elif face == "R":
            return -x
        elif face == "U":
            return y
        elif face == "D":
            return -y
        else:
            raise ArgumentError(f"Wrong face value: {face}")

    def get_up_on_face(self, face):
        """Returns up vector when looking at given face."""
        x, y, z = np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])
        if face in ["F", "R", "B", "L"]:
            return y
        elif face == "U":
            return z
        elif face == "D":
            return -z
        else:
            raise ArgumentError(f"Wrong face value: {face}")

    @staticmethod
    def get_face_for_normal(normal):
        [x, y, z] = normal
        if x > 0.9:
            return "L"
        elif x < -0.9:
            return "R"
        elif y > 0.9:
            return "U"
        elif y < -0.9:
            return "D"
        elif z > 0.9:
            return "B"
        elif z < -0.9:
            return "F"
        else:
            raise ValueError(f"No face for normal {normal}")

    def get_cubes_on_face(self, face):
        """Returns the 9 cubes on given face, ordered from top_left to bottom right."""
        normal = self.get_normal(face)
        up = self.get_up_on_face(face)
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
            normal = self.get_normal(face)
            for c in cubes:
                vect = c.rotation.inv().apply(normal)
                letter = self.get_face_for_normal(vect)
                state_str += letter
        return state_str

    def move(self, f):
        self.history_moves.append(f)
        face = f[0]
        reverse = "'" in f
        double = "2" in f
        cubes = self.get_cubes_on_face(face)
        normal = self.get_normal(face)
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

    def load_state(self, state_str):
        # Check valid
        try:
            kociemba.solve(state_str)
        except ValueError as e:
            raise ValueError(f"Invalid state string {state_str}")
        # Need to change cubes colors, as if gluing stickers
        for i, face in enumerate(["U", "R", "F", "D", "L", "B"]):
            cubes = self.get_cubes_on_face(face)
            normal = self.get_normal(face)
            for j, cube in enumerate(cubes):
                vect = cube.rotation.inv().apply(normal)
                f = self.get_face_for_normal(vect)
                # TODO find rotation for cube then apply colors

        self.state_string = state_str
        self.history_moves = []


if __name__ == '__main__':
    cube = RubiksCubeState()
    cube.shuffle(40)
    state = cube.compute_state_string()
    print("State", state)
    solution = kociemba.solve(state)
    print("Applying solution", solution)
    for move in solution.split(" "):
        cube.move(move)
    print(cube.compute_state_string())
