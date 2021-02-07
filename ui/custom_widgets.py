from tkinter import *
from tkinter.font import nametofont, BOLD


class WrappedLabel(Label):
    def __init__(self, master, text, **kwargs):
        self._txt = text
        super().__init__(master, **kwargs)
        self.bind('<Configure>', self.on_configure)

    def _update_text(self, max_width):
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

    def on_configure(self, event):
        self._update_text(event.width)


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


class MoveButton(Button):
    def __init__(self, master, face, reverse=False, **kwargs):
        image_path = "images/rot_" + face
        if reverse: image_path += "'"
        image_path += ".png"
        self.image = PhotoImage(file=image_path)

        super().__init__(master, image=self.image, bd=0, **kwargs)
        # TODO constrain dimensions / default font size

    def pack(self, **kwargs):
        kwargs = {"padx": 4, "pady": 4, **kwargs}
        super().pack(**kwargs)


class SolverControls(Frame):
    def __init__(self, master, name, **kwargs):
        super().__init__(master, **kwargs)
        self.title = Label(self, text=name, font=("Arial", 15))
        self.title.pack()
        todo = Label(self, text="TODO...", background="yellow")
        todo.pack()
        # TODO add name / buttons / loader / moves count / suggested moves

