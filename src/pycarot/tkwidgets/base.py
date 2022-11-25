import os
import tkinter as tk
from abc import ABC, abstractmethod
from enum import Enum, auto

import pycarot.tkwidgets.xmlparser as style


class WindowPosition(Enum):
    CenterScreen = auto()
    CenterOwner = auto()


class WindowBase(ABC, tk.Misc, tk.Wm):
    @property
    def width(self) -> int:
        return self.winfo_width()

    @property
    def height(self) -> int:
        return self.winfo_height()

    @property
    def x(self) -> int:
        return self.winfo_x()

    @property
    def y(self) -> int:
        return self.winfo_y()

    def move(self, x: int, y: int) -> None:
        if x > 0 and y > 0:
            self.wm_geometry(f"+{x}+{y}")

    def resize(self, width: int, height: int) -> None:
        if width > 0 and height > 0:
            self.wm_geometry(f"{width}x{height}")

    @abstractmethod
    def show(self, position: WindowPosition = None) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


def set_window_position(
    window: WindowBase,
    position: WindowPosition,
    parent: WindowBase = None,
) -> None:
    window.update()
    if position == WindowPosition.CenterScreen:
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        x = int(w / 2 - window.width / 2)
        y = int(h / 2 - window.height / 2)
        window.move(x, y)
    elif position == WindowPosition.CenterOwner:
        w, h = parent.width, parent.height
        x = parent.x + int(w / 2 - window.width / 2)
        y = parent.y + int(h / 2 - window.height / 2)
        window.move(x, y)


class MainWindow(tk.Tk, WindowBase):
    def __init__(
        self,
        title: str = None,
        icon: str = None,
        *args,
        **kwds,
    ) -> None:
        WindowBase.__init__(self)
        tk.Tk.__init__(self, *args, **kwds)
        self.wm_protocol("WM_DELETE_WINDOW", self.close)
        style.initialize("src\pycarot\tkwidgets\images")
        if title:
            self.wm_title(title)
        if icon and os.path.isfile(icon):
            self.wm_iconbitmap(icon)

    def show(self, position: WindowPosition = None) -> None:
        set_window_position(self, position)
        self.mainloop()

    def close(self) -> None:
        self.quit()


class Window(tk.Toplevel, WindowBase):
    def __init__(
        self,
        parent: WindowBase,
        title: str = None,
        icon: str = None,
    ) -> None:
        WindowBase.__init__(self)
        self._parent = parent
        self._title = title
        self._icon = icon

    def show(self, position: WindowPosition = None) -> None:
        tk.Toplevel.__init__(self, self._parent)
        self.wm_protocol("WM_DELETE_WINDOW", self.close)
        if self._title:
            self.wm_title(self._title)
        if self._icon and os.path.isfile(self._icon):
            self.wm_iconbitmap(self._icon)
        set_window_position(self, position, self._parent)

    def close(self) -> None:
        self.destroy()


class Dialog(Window):
    @property
    def result(self) -> bool:
        return self._result

    @result.setter
    def result(self, value: bool) -> None:
        self._result = value

    def exec(self, position: WindowPosition = None) -> bool:
        self.show(position)
        self._result = False
        self.grab_set()
        self.wait_window()
        return self.result

    def close(self) -> None:
        self.grab_release()
        Window.destroy(self)

    def accept(self) -> None:
        self.result = True
        self.close()

    def reject(self) -> None:
        self.result = False
        self.close()
