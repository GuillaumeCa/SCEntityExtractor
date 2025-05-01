import shutil
from tkinter import messagebox

def check_tools():
    texconv = shutil.which("texconv")
    cgfconv = shutil.which("cgf-converter")

    if texconv is None:
        messagebox.showerror("Error", "texconv tool was not found. Add it to your Path environment variable.")
        exit(1)

    if cgfconv is None:
        messagebox.showerror("Error", "cgf-converter tool was not found. Add it to your Path environment variable.")
        exit(1)