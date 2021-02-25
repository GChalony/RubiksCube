import kociemba

from rubiks_cube.rubikscube import RubiksCube


class KociembaSolver:
    def __init__(self):
        self._solution = None

    def get_next_move(self):
        return self._solution.split(" ")[0] if not self.is_solved() else None

    def get_all_moves(self):
        return self._solution.split(" ") if not self.is_solved() else []

    def is_solved(self):
        return len(self._solution) == 0

    def compute_solution(self, state, callback=None):
        if state == RubiksCube.SOLVED_STR:
            self._solution = ""
            return
        solution = kociemba.solve(state)
        self._solution = solution
        if callback is not None:
            callback(solution)