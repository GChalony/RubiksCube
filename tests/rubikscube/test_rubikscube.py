from rubiks_cube.rubikscube import RubiksCube


def test_compute_state_string():
    cube = RubiksCube()
    cube._compute_state_string()
    assert cube.state_string == RubiksCube.SOLVED_STR


def test_move():
    cube = RubiksCube()
    # Rotate on face
    cube.move("F")
    # Check state_str
    assert cube.state_string == "UUUUUULLLURRURRURRFFFFFFFFFRRRDDDDDDLLDLLDLLDBBBBBBBBB"
    cube.move("D")
    cube.move("L'")
    cube.move("L")
    cube.move("D'")
    cube.move("F'")
    assert cube.is_solved()


def test_load_state():
    # Create shuffled cube
    c = RubiksCube()
    c.shuffle()
    # Load its state
    ss = c.state_string
    c.load_state(ss)
    c._compute_state_string()
    # Compare
    assert ss == c.state_string

    c.load_state("UUUUUULLLURRURRURRFFFFFFFFFRRRDDDDDDLLDLLDLLDBBBBBBBBB")
    c.move("F'")
    assert c.is_solved()
