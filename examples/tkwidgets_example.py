import tkinter as tk
from tkinter import ttk

from pycarot.tkwidgets import base


shell = base.MainWindow()
shell.wm_minsize(500, 300)

frame = ttk.Frame(shell)
frame.pack(fill=tk.BOTH, expand=True)

button = ttk.Button(frame, text="Normal")
button.pack()
button = ttk.Button(frame, text="Normal")
button.pack()
button = ttk.Button(frame, text="Normal")
button.pack()

button = ttk.Button(frame, text="Disabled", state=tk.DISABLED)
button.pack()

shell.show(base.WindowPosition.CenterScreen)
