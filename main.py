from objects import Floor, Destroyable, Turret
from fractions import Fraction
from PIL import Image, ImageTk
import tkinter as tk
import typing as tp
import json


WORLD_SIZE: tuple[float, float] = (1920, 1080)
PLACEABLE: list = [
    Floor((0, 0, 0, 0), (0, 0), (0, 0)),
    Destroyable((0, 0), 0, image_path="./images/destroyables/box.png", name="box"),
    Turret((0, 0), "AK47")
]


def from_rgb(rgb):
    """translates a rgb tuple of int to a tkinter friendly color code
    """
    r, g, b = rgb
    return f'#{r:02x}{g:02x}{b:02x}'


class Window(tk.Tk):
    world_bg: tuple = (100, 100, 200)
    now_frame: tk.Frame = ...
    icon_size: int = 128
    scale: float = 1

    currently_placing: tk.Canvas
    aspect_ratio: tuple[int, int]
    placed_objects: list
    images: list[Image]

    def __init__(self) -> None:
        super().__init__()

        # mutable defaults
        tmp = Fraction(*WORLD_SIZE)
        self.aspect_ratio = tmp.numerator, tmp.denominator
        self.currently_placing = tk.Canvas(self)
        self.placed_objects = []
        self.images = []

        # set window options
        self.title("World Editor")
        self.attributes("-fullscreen", True)

        # bind shortcuts
        self.bind("<F11>", lambda _event: self.attributes("-fullscreen", True))
        self.bind('<Alt-Key-F4>', self.end)
        self.bind("<Escape>", self.end)

        # creat toplevel
        self.object_settings = tk.Toplevel(self)
        self.object_settings.bind("<Escape>", self.close_options)
        self.object_settings.bind("<FocusOut>", self.close_options)
        self.object_settings.protocol("WM_DELETE_WINDOW", self.close_options)
        self.object_settings.title("Object Settings")
        self.object_settings.withdraw()

        # initialize object options window
        self.object_type = tk.Label(self.object_settings, text="Type")
        self.object_type.grid(row=0, column=0)

        # create frames
        self.main_frame = tk.Frame(self, bg="black")

        # create canvases
        self.objects_can = tk.Canvas(self.main_frame, bg="gray24")
        self.game_can_center = tk.Canvas(self.main_frame)
        self.game_can = tk.Canvas(self.game_can_center, bg=from_rgb(self.world_bg))

        # pack canvases
        self.objects_can.grid(column=0, row=0, sticky="nsew")
        self.game_can_center.grid(column=1, row=0, sticky="nsew")
        self.game_can_center.grid_columnconfigure(0, weight=1)
        self.game_can_center.grid_rowconfigure(0, weight=1)
        self.game_can.grid()

        # configure columns
        self.main_frame.grid_rowconfigure(0, weight=1, pad=0)
        self.main_frame.grid_columnconfigure(0, weight=0, pad=0)
        self.main_frame.grid_columnconfigure(1, weight=1, pad=3)

        img = tk.PhotoImage(file="./images/characters/turret/turret.png")
        self.objects_can.create_image(100, 100, image=img)

        # initial functions
        self.draw_placeable()
        self.show_frame(self.main_frame)
        self.update_game_frame()

        self.focus_set()

    @property
    def game_window_size(self) -> tuple[float, float]:
        self.update_idletasks()

        max_val = max(self.aspect_ratio)
        max_ind = self.aspect_ratio.index(max_val)
        if max_ind == 0:
            val1 = self.game_can_center.winfo_width()
            val2 = val1 * (self.aspect_ratio[1] / self.aspect_ratio[0])

            return val1, val2

        else:
            val2 = self.game_can_center.winfo_height()
            val1 = val2 * (self.aspect_ratio[0] / self.aspect_ratio[1])

            return val1, val2

    def show_frame(self, frame: tk.Frame) -> None:
        if self.now_frame is not ...:
            self.now_frame.pack_forget()

        frame.pack(fill=tk.BOTH, expand=True)
        self.now_frame = frame

    def draw_placeable(self) -> None:
        for element in PLACEABLE:
            tmp_can = tk.Canvas(self.objects_can)
            tmp_can.pack(padx=10, pady=10)

            tmp_can.bind("<Button-1>", lambda _event, x=type(element): self.place_object(x))

            half = 32 + self.icon_size / 2
            if "image_path" in element.__dict__:
                img = Image.open(element.image_path)
                img = img.resize((self.icon_size, self.icon_size), Image.Resampling.LANCZOS)
                img = ImageTk.PhotoImage(img)
                self.images.append(img)

                tmp_can.create_image(half, half, image=img)
                continue

            tk.Label(tmp_can, text=type(element).__name__, font=("Times New Roman", 20)).place(x=half, y=half)

    def update_game_frame(self) -> None:
        width, height = self.game_window_size
        self.game_can.config(width=width, height=height)

    def edit_object(self, obj) -> None:
        # edit options
        self.object_type["text"] = f"Type: {obj.__name__}"

        # open window
        self.object_settings.deiconify()

    def place_object(self, obj) -> None:
        print(f"placing {obj}")
        self.edit_object(obj)

    def close_options(self, *_trash) -> None:
        self.object_settings.withdraw()

    def export_world(self, name: str) -> None:
        out: dict[str, tp.Any] = {
            "name": name,
            "background": list(self.world_bg) + [255],
            "objects": []
        }

        for element in self.placed_objects:
            tmp: dict[str, tp.Any] = {
                "type": type(element).__name__
            }
            for attribute in element.__dict__.keys():
                attribute: str
                if not attribute.startswith("__"):
                    tmp[attribute] = element.__dict__[attribute]

            out["objects"].append(tmp)

        with open(name+".json", "w") as outfile:
            json.dump(out, outfile, indent=4)

    def end(self, *_trash) -> None:
        self.export_world(name="backup")
        self.destroy()


if __name__ == "__main__":
    w = Window()
    w.mainloop()
