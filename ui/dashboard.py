import tkinter as tk
from threading import Thread
from time import sleep
from tkinter import font

from ui.custom_widgets import SectionTitle, ArrowButton, MoveButton, WrappedLabel, SolverControls


class Dashboard(tk.Tk):
    # TODO add tooltips
    def __init__(self):
        super().__init__()
        self.title("RubiksCube controls")
        self.geometry("300x700+1300+200")

        # State controls
        self.state_label = SectionTitle(self, text='State')
        self.state_label.pack(fill=tk.X, ipady=5)
        sf = tk.Frame(self)
        state = WrappedLabel(sf, text="DRLUUBFDRLUUBFDRLUUBFDRLUUBF", justify=tk.LEFT, anchor=tk.W)
        copy_logo = tk.PhotoImage(file="images/copy.png")
        copy = tk.Button(sf, image=copy_logo, bd=0)
        copy.image = copy_logo
        state.pack(side=tk.LEFT, fill=tk.X, expand=True)
        copy.pack(side=tk.LEFT)
        sf.pack(fill=tk.X)
        state.pack()

        # View controls
        self.view_label = SectionTitle(self, text='View')
        self.view_label.pack(fill=tk.X, ipady=5)
        frame = tk.Frame()
        reset = tk.Button(frame, text="Reset", font=("Arial", 10, tk.font.ITALIC))
        b1 = ArrowButton(frame, type="left")
        b2 = ArrowButton(frame, type="up")
        b3 = ArrowButton(frame, type="down")
        b4 = ArrowButton(frame, type="right")
        reset.pack(side=tk.LEFT)
        b1.pack(side=tk.LEFT)
        b2.pack(side=tk.LEFT)
        b3.pack(side=tk.LEFT)
        b4.pack(side=tk.LEFT)
        frame.pack()

        # Moves controls
        self.moves_label = SectionTitle(self, text='Moves')
        self.moves_label.pack(fill=tk.X, ipady=5)
        mf = tk.Frame(self)
        move_F = MoveButton(mf, face="F")
        move_B = MoveButton(mf, face="B")
        move_R = MoveButton(mf, face="R")
        move_L = MoveButton(mf, face="L")
        move_U = MoveButton(mf, face="U")
        move_D = MoveButton(mf, face="D")
        move_F.pack(side=tk.LEFT)
        move_B.pack(side=tk.LEFT)
        move_R.pack(side=tk.LEFT)
        move_L.pack(side=tk.LEFT)
        move_U.pack(side=tk.LEFT)
        move_D.pack(side=tk.LEFT)
        mf.pack()
        mf = tk.Frame(self)
        move_F = MoveButton(mf, face="F", reverse=True)
        move_B = MoveButton(mf, face="B", reverse=True)
        move_R = MoveButton(mf, face="R", reverse=True)
        move_L = MoveButton(mf, face="L", reverse=True)
        move_U = MoveButton(mf, face="U", reverse=True)
        move_D = MoveButton(mf, face="D", reverse=True)
        move_F.pack(side=tk.LEFT)
        move_B.pack(side=tk.LEFT)
        move_R.pack(side=tk.LEFT)
        move_L.pack(side=tk.LEFT)
        move_U.pack(side=tk.LEFT)
        move_D.pack(side=tk.LEFT)
        mf.pack()

        # Solving controls
        self.solving_label = SectionTitle(self, text='Solving')
        self.solving_label.pack(fill=tk.X, ipady=5)
        basic = SolverControls(self, "Basic Solver")
        basic.pack()
        kocima = SolverControls(self, "Kocima Solver")
        kocima.pack()

if __name__=="__main__":
    dash = Dashboard()
    dash.mainloop()


