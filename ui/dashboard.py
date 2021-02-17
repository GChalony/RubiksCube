import tkinter as tk
from tkinter import font

import Pmw
import numpy as np

from rubikscube.core import state_str_to_state_description
from rubikscube.rubikscube import RubiksCube
from rubikscube.solvers.kociemba_solver import KociembaSolver
from ui.custom_widgets import SectionTitle, ArrowButton, MoveButton, WrappedLabel, SolverControls, ToggleButton2
from ui.events_hub import EventsHub, Event


class Dashboard(tk.Tk):
    def __init__(self, event_hub: EventsHub):
        super().__init__()
        self.kociemba_solver = KociembaSolver()

        self.state_tooltip = Pmw.Balloon(self)
        self.state_tooltip.configure(label_font=("Courier", 8))
        self.tooltip = Pmw.Balloon(self)
        self.event_hub = event_hub
        self.title("RubiksCube controls")
        self.geometry("300x700+1200+200")
        self._create_state()
        self._create_view()
        self._create_controls()
        self._create_solvers()
        self._add_events_raisers()
        self._add_listeners()

    def _create_state(self):
        # State controls
        self.state_label = SectionTitle(self, text='State')
        self.state_label.pack(fill=tk.X, ipady=5)
        sf = tk.Frame(self)
        self.state = WrappedLabel(sf, text=RubiksCube.SOLVED_STR, justify=tk.LEFT)
        self.state_tooltip.bind(self.state, state_str_to_state_description(RubiksCube.SOLVED_STR))
        copy_logo = tk.PhotoImage(file="images/copy.png")
        self.copy_button = tk.Button(sf, image=copy_logo, bd=0)
        self.copy_button.image = copy_logo
        self.tooltip.bind(self.copy_button, "Copy to clipboard")
        self.state.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.copy_button.pack(side=tk.LEFT)
        sf.pack(fill=tk.X)
        self.shuffle = tk.Button(self, text="Shuffle")  # TODO connect
        self.shuffle.pack()
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
        self.rot_toggle = ToggleButton2(frame, text="rot", toggled=True)
        self.tooltip.bind(self.reset, "Reset view (Esc)")
        self.tooltip.bind(self.left, "Rotate left (Left arrow)")
        self.tooltip.bind(self.up, "Rotate up (Up arrow)")
        self.tooltip.bind(self.down, "Rotate down (Down arrow)")
        self.tooltip.bind(self.right, "Rotate right (Right arrow)")
        self.tooltip.bind(self.rot_toggle, "Toggle cube rotation (Space)")
        self.reset.pack(side=tk.LEFT)
        self.left.pack(side=tk.LEFT)
        self.up.pack(side=tk.LEFT)
        self.down.pack(side=tk.LEFT)
        self.right.pack(side=tk.LEFT)
        self.rot_toggle.pack(side=tk.LEFT)
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
        self.tooltip.bind(self.move_F, "Move Front face \nclockwise (F)")
        self.tooltip.bind(self.move_B, "Move Back face \nclockwise (B)")
        self.tooltip.bind(self.move_R, "Move Right face \nclockwise (R)")
        self.tooltip.bind(self.move_L, "Move Left face \nclockwise (L)")
        self.tooltip.bind(self.move_U, "Move Up face \nclockwise (U)")
        self.tooltip.bind(self.move_D, "Move Down face \nclockwise (D)")
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
        self.tooltip.bind(self.move_Fr, "Move Front face \ncounterclockwise (Maj + F)")
        self.tooltip.bind(self.move_Br, "Move Back face \ncounterclockwise (Maj + B)")
        self.tooltip.bind(self.move_Rr, "Move Right face \ncounterclockwise (Maj + R)")
        self.tooltip.bind(self.move_Lr, "Move Left face \ncounterclockwise (Maj + L)")
        self.tooltip.bind(self.move_Ur, "Move Up face \ncounterclockwise (Maj + U)")
        self.tooltip.bind(self.move_Dr, "Move Down face \ncounterclockwise (Maj + D)")
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
        self.kociemba = SolverControls(self, "Kociemba Solver")
        self.tooltip.bind(self.kociemba, "Kociemba solution")
        self.kociemba.pack()

    def copy_state_to_clipboard(self, event=None):
        state = self.state.get_text()
        self.clipboard_clear()
        self.clipboard_append(state)

    def on_close(self):
        # Override close protocol to send close signal
        self.event_hub.raise_event(Event(origin=Event.TKINTER, type=Event.QUIT))

    def change_state_label(self, state_str):
        self.state.set_text(state_str)
        state_description = state_str_to_state_description(state_str)
        self.state_tooltip.bind(self.state, state_description)

    def on_animation_finished(self, event):
        self.change_state_label(event.state_str)
        if event.is_solved:
            self.kociemba.edit_solution("Solved!", fg="green")
        else:
            self.kociemba_solver.compute_solution(event.state_str,
                                                  lambda sol: self.kociemba.edit_solution(sol, fg="black"))

    def apply_all_moves(self, moves):
        for move in moves:
            self.event_hub.raise_event(
                Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face=move)
            )

    def _add_events_raisers(self):
        # Adds all callbacks to hook Tkinter events to event_hub
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.copy_button.bind("<Button>", self.copy_state_to_clipboard)

        angle_move = np.radians(10)
        self.reset.bind("<Button>",
                        lambda ev: self.event_hub.raise_event(
                            Event(origin=Event.TKINTER, type=Event.CAMERA_RESET)))
        self.left.bind("<Button>",
                       lambda ev: self.event_hub.raise_event(
                           Event(origin=Event.TKINTER, type=Event.CAMERA_MOVE, direction="LEFT", angle=angle_move)))
        self.right.bind("<Button>",
                        lambda ev: self.event_hub.raise_event(
                            Event(origin=Event.TKINTER, type=Event.CAMERA_MOVE, direction="RIGHT", angle=angle_move)))
        self.up.bind("<Button>",
                     lambda ev: self.event_hub.raise_event(
                         Event(origin=Event.TKINTER, type=Event.CAMERA_MOVE, direction="UP", angle=angle_move)))
        self.down.bind("<Button>",
                       lambda ev: self.event_hub.raise_event(
                           Event(origin=Event.TKINTER, type=Event.CAMERA_MOVE, direction="DOWN", angle=angle_move))
                       )
        self.rot_toggle.bind("<Button>",
                             lambda ev: self.event_hub.raise_event(Event(origin=Event.TKINTER, type=Event.CAMERA_TOGGLE_ROT)))

        self.move_F.bind("<Button>",
                         lambda ev: self.event_hub.raise_event(
                             Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face="F")))
        self.move_B.bind("<Button>",
                         lambda ev: self.event_hub.raise_event(
                             Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face="B")))
        self.move_U.bind("<Button>",
                         lambda ev: self.event_hub.raise_event(
                             Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face="U")))
        self.move_D.bind("<Button>",
                         lambda ev: self.event_hub.raise_event(
                             Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face="D")))
        self.move_L.bind("<Button>",
                         lambda ev: self.event_hub.raise_event(
                             Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face="L")))
        self.move_R.bind("<Button>",
                         lambda ev: self.event_hub.raise_event(
                             Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face="R")))
        self.move_Fr.bind("<Button>",
                          lambda ev: self.event_hub.raise_event(
                              Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face="F'")))
        self.move_Br.bind("<Button>",
                          lambda ev: self.event_hub.raise_event(
                              Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face="B'")))
        self.move_Ur.bind("<Button>",
                          lambda ev: self.event_hub.raise_event(
                              Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face="U'")))
        self.move_Dr.bind("<Button>",
                          lambda ev: self.event_hub.raise_event(
                              Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face="D'")))
        self.move_Lr.bind("<Button>",
                          lambda ev: self.event_hub.raise_event(
                              Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face="L'")))
        self.move_Rr.bind("<Button>",
                          lambda ev: self.event_hub.raise_event(
                              Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE, face="R'")))

        self.kociemba.forward.bind("<Button>",
                                   lambda ev: self.event_hub.raise_event(
                                       Event(origin=Event.TKINTER, type=Event.CUBE_MOVE_FACE,
                                             face=self.kociemba_solver.get_next_move())
                                   ))
        self.kociemba.fastforward.bind("<Button>",
                                   lambda ev: self.apply_all_moves(self.kociemba_solver.get_all_moves()))

    def _add_listeners(self):
        self.event_hub.add_callback(Event.QUIT, lambda ev: self.quit())
        self.event_hub.add_callback(Event.ANIMATIONFINISHED, self.on_animation_finished)
        self.event_hub.add_callback(Event.CAMERA_TOGGLE_ROT, self.rot_toggle.toggle)
