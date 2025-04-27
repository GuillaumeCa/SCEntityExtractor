import signal
import sys
import logging
import threading
import json
import os
import subprocess
import shutil
from pathlib import Path

import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox

from scdatatools.sc import StarCitizen
from scdatatools.sc.blueprints.generators.datacore_entity import (
    blueprint_from_datacore_entity,
)


# logging.getLogger().setLevel(logging.DEBUG)


SC_INSTALL_PATH="C:/Program Files/Roberts Space Industries/StarCitizen/LIVE"

CACHE_DIR=".sccache"

RECORDS_ROOT_PATH = "libs/foundry/records/"
VEHICLES_ROOT = f"{RECORDS_ROOT_PATH}entities/groundvehicles"
SHIPS_ROOT = f"{RECORDS_ROOT_PATH}entities/spaceships"

OUTPUT="./extract"


def check_tools():
    texconv = shutil.which("texconv")
    cgfconv = shutil.which("cgf-converter")

    print(texconv, cgfconv)
    if texconv is None:
        messagebox.showerror("Error", "texconv tool was not found. Add it to your Path environment variable.")
        exit(1)
    
    if cgfconv is None:
        messagebox.showerror("Error", "cgf-converter tool was not found. Add it to your Path environment variable.")
        exit(1)

check_tools()

from scdatatools.engine.chunkfile.converter import printConverter

printConverter()


def setup_config():
    global SC_INSTALL_PATH

    # Path where you want your JSON file
    file_path = Path("settings.json")

    # Default content you want inside the JSON
    default_data = {
        "SC_path": SC_INSTALL_PATH,
    }

    # Check if the file exists
    if not file_path.exists():
        # Create it with default data
        with open(file_path, "w") as f:
            json.dump(default_data, f, indent=4)
        print(f"Created {file_path}")
    else:
        print(f"{file_path} already exists.")

    # You can now safely load or modify the file
    with open(file_path, "r") as f:
        data = json.load(f)
        print("Loaded config: ", data)

        SC_INSTALL_PATH = data["SC_path"]



setup_config()


# Set appearance
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

def handle_ctrl_c(sig, frame):
    print("\nCtrl+C detected! Exiting gracefully...")
    root.destroy()
    sys.exit(0)

# Attach the signal handler
signal.signal(signal.SIGINT, handle_ctrl_c)


sc = StarCitizen(SC_INSTALL_PATH, cache_dir=CACHE_DIR)
print("Loading Datacore")
assert sc.datacore is not None

def search():
    query = entry.get()

    # filetree = sc.p4k.file_tree
    
    for i in treeview.get_children():
        treeview.delete(i)

    entity_names = []
    for entKey in sc.datacore.entities:
        if query.lower() in entKey.lower():
            entity_names.append(sc.datacore.entities[entKey])
    
    show_entities(entity_names)

def show_entities(entities):
    for ent in entities:
        category = ""
        filename = entities[ent].filename
        if filename.startswith(VEHICLES_ROOT):
            category = "Vehicule"
        elif filename.startswith(SHIPS_ROOT):
            category = "Ship"
        else:
            continue


        treeview.insert("", "end", text=ent, values=(category))


    # listbox.delete("1.0", ctk.END)
    
    # build_tree(filetree)

    # for folder in folders:
    #     print(folder)
    #     listbox.insert(ctk.END, folder)

def build_tree(datatree: dict, parent: str = ""):
    for key in datatree:
        val = datatree[key]
        if type(val) is dict:
            if len(val.keys()) > 0:
                subtree = treeview.insert(parent, "end", text=key, values=("Folder"))
                build_tree(val, subtree)
            else:
                treeview.insert(parent, "end", text=key, values=("File"))

selected_item_data = None

def on_item_selected(event):
    global selected_item_data

    selected_item = treeview.selection()  # This returns a tuple of selected item IDs
    if selected_item:
        item_id = selected_item[0]
        item = treeview.item(item_id)  # Get item data
        print("Selected:", item["text"], item["values"])
        selected_item_data = item

        export_btn.configure(state="normal")


print("Starting app")


# Main window
root = ctk.CTk()
root.title("SC Entity Extractor")
root.geometry("500x800")


# Title Label
title_label = ctk.CTkLabel(root, text="SC Entity Extractor", font=("Helvetica", 24))
title_label.pack(pady=20)

# # Entry (TextField)
# entry = ctk.CTkEntry(root, width=300, height=40, font=("Helvetica", 14))
# entry.pack(pady=10)

# # Rounded Search Button
# search_button = ctk.CTkButton(root, text="Search", width=150, height=40, corner_radius=20, command=search)
# search_button.pack(pady=10)


style = ttk.Style()
style.configure("Treeview", font=("Helvetica", 14))  # <--- Set font and size
style.configure("Treeview.Heading", font=("Helvetica", 16, "bold"))  # <--- Heading font
style.configure("Treeview", rowheight=24)


# Tree for results

# listbox = ctk.CTkTextbox(root, width=400, height=150, font=("Helvetica", 12))
# listbox.pack(pady=20)

treeview = ttk.Treeview(root)

treeview["columns"] = ("Type")
treeview.column("#0", width=150, minwidth=100)  # Tree column
treeview.column("Type", anchor="w", width=120)

treeview.heading("#0", text="Item", anchor="w")
treeview.heading("Type", text="Type", anchor="w")


treeview.pack(pady=10, padx=20, fill="both", expand=True)

treeview.bind("<<TreeviewSelect>>", on_item_selected)



def export():
    # Set progress bar to visible
    progressbar.pack(padx=20, pady=10, fill="x", expand=True)
    progressbar.start()
    export_label.pack(pady=10)

    export_btn.pack_forget()

    entity_name = selected_item_data["text"]
    selected = sc.datacore.entities[entity_name]

    output = Path(f"{OUTPUT}/{selected.name}")
    output.mkdir(parents=True, exist_ok=True)

    if os.path.isfile("debug.log"):
        os.remove("debug.log")

    def exportprogress(msg="", progress: int=None, total: int=None, level=logging.INFO, exc_info=None):
        if msg != "":
            export_label.configure(text=msg)

        with open("debug.log", "a") as f:
            f.write(msg + "\n")

    print("Generating blueprint from entity")
    exportprogress(msg="Generating blueprint...")
    bp = blueprint_from_datacore_entity(sc, selected, monitor=exportprogress)

    exportprogress(msg="Saving blueprint...")
    with open(output / f"{bp.name}.scbp", "w") as o:
        bp.dump(o)

    exportprogress(msg="Extracting blueprint...")
    print("Extracting blueprint")
    bp.extract(
        outdir=output, 
        auto_convert_textures=True, 
        auto_convert_models=True, 
        overwrite=True
    )
    print("Done!")

    # Hide the progress bar again
    progressbar.pack_forget()
    export_label.pack_forget()

    
    # Show export button again
    export_btn.pack(pady=10)
    progressbar.stop()

    messagebox.showinfo("Information", f"Your model {entity_name} was exported successfully !")


def start_export():
    if selected_item_data != None:
        threading.Thread(target=export, daemon=True).start()



export_btn = ctk.CTkButton(root, text="Export", width=100, height=40, corner_radius=10, command=start_export)
export_btn.configure(state="disabled")
export_btn.pack(pady=10)

export_label = ctk.CTkLabel(root, text="Exporting...", font=("Helvetica", 12))

progressbar = ctk.CTkProgressBar(root, mode="undeterminate")


show_entities(sc.datacore.entities)

root.mainloop()

