import kociemba

from rubiks_cube.rubikscube import RubiksCube


class KociembaSolver:
    def __init__(self):
        self._solution = None

    @property
    def solution_str(self):
        return " ".join(self._solution)

    def get_next_move(self, i):
        return self._solution[i] if not self.is_solved() else None

    def get_all_moves(self):
        return self._solution if not self.is_solved() else []

    def is_solved(self):
        return len(self._solution) == 0

    def compute_solution(self, state, callback=None):
        if state == RubiksCube.SOLVED_STR:
            self._solution = []
        else:
            solution = kociemba.solve(state).split(" ")
            self._solution = solution
        if callback is not None:
            callback(self._solution)
