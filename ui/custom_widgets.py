from tkinter import *
from tkinter.font import nametofont, BOLD


class WrappedLabel(Label):
    # TODO double click to edit state
    def __init__(self, master, text, **kwargs):
        self._txt = text
        super().__init__(master, **kwargs)
        self.bind('<Configure>', self._update_text)

    def _update_text(self, event=None):
        max_width = self.master.winfo_width() - 44  # Hardcoded button width
        font = nametofont(self.cget("font"))
        text = self._txt

        actual_width = font.measure(text)
        if actual_width <= max_width:
            self.configure(text=text)
        else:
            while actual_width > max_width and len(text) > 1:
                text = text[:-1]
                actual_width = font.measure(text + "...")
            self.configure(text=text + "...")

    def get_text(self):
        return self._txt

    def set_text(self, txt):
        self._txt = txt
        self.config(text=txt)


class SectionTitle(Frame):
    """Title widget to separate controls sections"""
    def __init__(self, master, text, **kwargs):
        super().__init__(master, background=None, **kwargs)
        self.h1 = Canvas(self, width=30, height=3, bg="gray")
        self.txt = Label(self, text=text, font=("Arial", 15, BOLD))
        self.h2 = Canvas(self, width=30, height=3, bg="gray")
        self.h1.pack(side=LEFT, padx=10)
        self.txt.pack(side=LEFT, padx=10)
        self.h2.pack(side=LEFT, fill=X, expand=True, padx=10)


class ArrowButton(Button):
    def __init__(self, master, type, **kwargs):
        image_path = f"images/{type}.png"
        self.image = PhotoImage(file=image_path)  # Downsampled
        super().__init__(master, image=self.image, bd=0, **kwargs)

    def pack(self, **kwargs):
        kwargs = {"padx": 4, "pady": 4, **kwargs}
        super().pack(**kwargs)


class ImagedButton(Button):
    def __init__(self, master, image_path, **kwargs):
        self.image = PhotoImage(file=image_path)
        super().__init__(master, image=self.image, bd=0, **kwargs)

    def pack(self, **kwargs):
        kwargs = {"padx": 4, "pady": 4, **kwargs}
        super().pack(**kwargs)


class MoveButton(ImagedButton):
    def __init__(self, master, face, reverse=False, **kwargs):
        image_path = "images/rot_" + face
        if reverse: image_path += "'"
        image_path += ".png"
        super().__init__(master, image_path=image_path, **kwargs)


class SolverControls(Frame):
    def __init__(self, master, name, **kwargs):
        super().__init__(master, **kwargs)
        self.title = Label(self, text=name, font=("Arial", 15))
        nf = Frame(self)
        n_moves_txt = Label(nf, text="Number of moves:")
        self.n_moves = Label(nf, text="0")
        n_moves_txt.pack(side=LEFT)
        self.n_moves.pack(side=LEFT)
        self.solution = Label(self, text="...", wraplength=150)
        controls = Frame(self)
        self.forward = ImagedButton(controls, image_path="images/forward2.png")
        self.fastforward = ImagedButton(controls, image_path="images/fastforward2.png")

        self.title.pack()
        nf.pack()
        self.solution.pack()
        self.forward.pack(side=LEFT)
        self.fastforward.pack(side=LEFT)
        controls.pack()

    def edit_solution(self, solution, fg=None):
        self.solution.config(text=solution)
        self.solution.config(fg=fg)
        self.n_moves.config(text=str(len(solution.split(" "))))


class ToggleButton2(Frame):
    def __init__(self, master, text, toggled=False):
        super().__init__(master, background="red", width=10)
        self._width = 25
        self._height = 20
        self._text = Label(self, text=text)
        self._canvas = Canvas(self, width=self._width, height=self._height)
        # self._text.pack()
        self._canvas.pack()
        self._toggled = False
        self.bind("<Button>", lambda ev: print("Clicked!"))
        self._callbacks = []
        self._draw()
        if toggled:
            self.toggle()

    def _draw(self):
        self._canvas.delete("all")
        w, h = self._width, self._height
        r = 8
        x = w - r - 1 if self._toggled else r + 1
        y = h // 2
        color = "black" if self._toggled else "grey"
        self._canvas.create_line(3, h//2, w-3, h//2, fill="gray", width=5, capstyle='round')
        self._canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, width=0)

    def toggle(self, event=None):
        self._toggled = not self._toggled
        self._draw()

    def bind(self, sequence=None, func=None, add=None):
        # Monkey patching to attach button bindings to canvas and not parent frame
        if "<Button" in sequence:
            self._canvas.bind(sequence, func, add)
        else:
            super().bind(sequence, func, add)


if __name__ == '__main__':
    tk = Tk()
    frame = Frame(tk, background="red", width=500, height=200)
    frame.bind("<Button>", lambda ev: print("Clicked!"))
    frame.pack()
    button = Button(frame, background="blue")
    button.bindtags(("mytag",) + button.bindtags())
    button.bind_class("mytag", "<Button>", lambda ev:print("Hello"))
    button.pack()
    tk.mainloop()
