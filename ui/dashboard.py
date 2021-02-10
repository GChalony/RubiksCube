import tkinter as tk
from tkinter import font

from events_controllers import NavigationController
from rubikscube import RubiksCube
from ui.custom_widgets import SectionTitle, ArrowButton, MoveButton, WrappedLabel, SolverControls


class Dashboard(tk.Tk):
    # TODO add tooltips
    def __init__(self, cube, view_controller):
        super().__init__()
        self.cube: RubiksCube = cube
        self.view_controller: NavigationController = view_controller
        self.title("RubiksCube controls")
        self.geometry("300x700+1200+200")
        self._create_state()
        self._create_view()
        self._create_controls()
        self._create_solvers()
        self._add_callbacks()

    def _create_state(self):
        # State controls
        self.state_label = SectionTitle(self, text='State')
        self.state_label.pack(fill=tk.X, ipady=5)
        sf = tk.Frame(self)
        self.state = WrappedLabel(sf, text="DRLUUBFDRLUUBFDRLUUBFDRLUUBF", justify=tk.LEFT, anchor=tk.W)
        copy_logo = tk.PhotoImage(file="images/copy.png")
        self.copy_button = tk.Button(sf, image=copy_logo, bd=0)
        self.copy_button.image = copy_logo
        self.state.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.copy_button.pack(side=tk.LEFT)
        sf.pack(fill=tk.X)
        self.state.pack()

    def _create_view(self):
        # View controls
        self.view_label = SectionTitle(self, text='View')
        self.view_label.pack(fill=tk.X, ipady=5)
        frame = tk.Frame()
        self.reset = tk.Button(frame, text="Reset", font=("Arial", 10, tk.font.ITALIC))
        self.left = ArrowButton(frame, type="left")
        self.up = ArrowButton(frame, type="up")
        self.down = ArrowButton(frame, type="down")
        self.right = ArrowButton(frame, type="right")
        self.reset.pack(side=tk.LEFT)
        self.left.pack(side=tk.LEFT)
        self.up.pack(side=tk.LEFT)
        self.down.pack(side=tk.LEFT)
        self.right.pack(side=tk.LEFT)
        frame.pack()

    def _create_controls(self):
        # Moves controls
        self.moves_label = SectionTitle(self, text='Moves')
        self.moves_label.pack(fill=tk.X, ipady=5)
        mf = tk.Frame(self)
        self.move_F = MoveButton(mf, face="F")
        self.move_B = MoveButton(mf, face="B")
        self.move_R = MoveButton(mf, face="R")
        self.move_L = MoveButton(mf, face="L")
        self.move_U = MoveButton(mf, face="U")
        self.move_D = MoveButton(mf, face="D")
        self.move_F.pack(side=tk.LEFT)
        self.move_B.pack(side=tk.LEFT)
        self.move_R.pack(side=tk.LEFT)
        self.move_L.pack(side=tk.LEFT)
        self.move_U.pack(side=tk.LEFT)
        self.move_D.pack(side=tk.LEFT)
        mf.pack()
        mf = tk.Frame(self)
        self.move_Fr = MoveButton(mf, face="F", reverse=True)
        self.move_Br = MoveButton(mf, face="B", reverse=True)
        self.move_Rr = MoveButton(mf, face="R", reverse=True)
        self.move_Lr = MoveButton(mf, face="L", reverse=True)
        self.move_Ur = MoveButton(mf, face="U", reverse=True)
        self.move_Dr = MoveButton(mf, face="D", reverse=True)
        self.move_Fr.pack(side=tk.LEFT)
        self.move_Br.pack(side=tk.LEFT)
        self.move_Rr.pack(side=tk.LEFT)
        self.move_Lr.pack(side=tk.LEFT)
        self.move_Ur.pack(side=tk.LEFT)
        self.move_Dr.pack(side=tk.LEFT)
        mf.pack()

    def _create_solvers(self):
        # Solving controls
        self.solving_label = SectionTitle(self, text='Solving')
        self.solving_label.pack(fill=tk.X, ipady=5)
        basic = SolverControls(self, "Basic Solver")
        basic.pack()
        kocima = SolverControls(self, "Kocima Solver")
        kocima.pack()

    def copy_state_to_clipboard(self, ev):
        state = self.state.get_text()
        self.clipboard_clear()
        self.clipboard_append(state)
        print("Copied!")

    def _add_callbacks(self):
        self.copy_button.bind("<Button>", self.copy_state_to_clipboard)

        self.reset.bind("<Button>", lambda ev: self.view_controller.reset_view())
        self.left.bind("<Button>", lambda ev: self.view_controller.start_move("LEFT"))
        self.right.bind("<Button>", lambda ev: self.view_controller.start_move("RIGHT"))
        self.up.bind("<Button>", lambda ev: self.view_controller.start_move("UP"))
        self.down.bind("<Button>", lambda ev: self.view_controller.start_move("DOWN"))

        self.move_F.bind("<Button>", lambda ev: self.cube.move_face("F"))
        self.move_B.bind("<Button>", lambda ev: self.cube.move_face("B"))
        self.move_U.bind("<Button>", lambda ev: self.cube.move_face("U"))
        self.move_D.bind("<Button>", lambda ev: self.cube.move_face("D"))
        self.move_L.bind("<Button>", lambda ev: self.cube.move_face("L"))
        self.move_R.bind("<Button>", lambda ev: self.cube.move_face("R"))
        self.move_Fr.bind("<Button>", lambda ev: self.cube.move_face("F", reverse=True))
        self.move_Br.bind("<Button>", lambda ev: self.cube.move_face("B", reverse=True))
        self.move_Ur.bind("<Button>", lambda ev: self.cube.move_face("U", reverse=True))
        self.move_Dr.bind("<Button>", lambda ev: self.cube.move_face("D", reverse=True))
        self.move_Lr.bind("<Button>", lambda ev: self.cube.move_face("L", reverse=True))
        self.move_Rr.bind("<Button>", lambda ev: self.cube.move_face("R", reverse=True))

