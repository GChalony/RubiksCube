import kociemba


class KociembaSolver:
    def solve(self, state, callback):
        result = kociemba.solve(state)
        callback(result)
