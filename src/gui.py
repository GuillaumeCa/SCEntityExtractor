import threading
import os
import sys
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from exporter import Exporter
from config import Config

class SCEntityExtractorApp:
    def __init__(self, config: Config):
        self.config = config
        self.exporter = Exporter(config)
        self.selected_item_data = None

        # Initialize GUI
        self.root = ctk.CTk()
        self.root.title("SC Entity Extractor")
        self.root.iconbitmap(self.resource_path('icon.ico'))
        self.root.geometry("500x800")

        self._setup_ui()


    def resource_path(self, relative_path: str):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def _setup_ui(self):
        # Title Label
        title_label = ctk.CTkLabel(self.root, text="SC Entity Extractor", font=("Helvetica", 24))
        title_label.pack(pady=20)

        # Search Textbox
        self.search_entry = ctk.CTkEntry(self.root, placeholder_text="Search", height=30)
        self.search_entry.pack(padx=10, pady=10, fill="x")
        self.search_entry.bind('<Key>', self.on_search_change)

        # Treeview
        self._setup_treeview()

        # Export Button
        self.export_btn = ctk.CTkButton(self.root, text="Export", width=100, height=40, corner_radius=10, command=self.start_export)
        self.export_btn.configure(state="disabled")
        self.export_btn.pack(pady=10)

        # Progress Bar and Label
        self.export_label = ctk.CTkLabel(self.root, text="Exporting...", font=("Helvetica", 12))
        self.progressbar = ctk.CTkProgressBar(self.root, mode="indeterminate")

    def _setup_treeview(self):
        style = ttk.Style()
        style.theme_use("vista")
        style.configure("Treeview", font=("Helvetica", 14), background="#404040", foreground="white", fieldbackground="#404040")
        style.configure("Treeview.Heading", font=("Helvetica", 16, "bold"), foreground="black")
        style.configure("Treeview", rowheight=30)

        frame = tk.Frame(self.root)
        frame.pack(pady=10, fill="both", expand=True)

        self.treeview = ttk.Treeview(frame)
        self.treeview["columns"] = ("Type")
        self.treeview.column("#0", width=200, minwidth=100)
        self.treeview.column("Type", anchor="w", width=60)
        self.treeview.heading("#0", text="Item", anchor="w")
        self.treeview.heading("Type", text="Type", anchor="w")
        self.treeview.pack(side=tk.LEFT, fill="both", expand=True)
        self.treeview.bind("<<TreeviewSelect>>", self.on_item_selected)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.treeview.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.treeview.configure(yscrollcommand=scrollbar.set)

    def on_search_change(self, event):
        search = self.search_entry.get()
        self.show_entities(search)

    def show_entities(self, filter=""):
        for child in self.treeview.get_children():
            self.treeview.delete(child)

        for ent, entity in self.exporter.get_entities(filter).items():
            self.treeview.insert("", "end", text=ent, values=(entity["category"]))

    def on_item_selected(self, event):
        selected_item = self.treeview.selection()
        if selected_item:
            item_id = selected_item[0]
            self.selected_item_data = self.treeview.item(item_id)
            self.export_btn.configure(state="normal")

    def start_export(self):
        if self.selected_item_data:
            threading.Thread(target=self.export, daemon=True).start()

    def export(self):
        self.progressbar.pack(padx=20, pady=10, fill="x", expand=True)
        self.progressbar.start()
        self.export_label.pack(pady=10)
        self.export_btn.pack_forget()

        entity_name = self.selected_item_data["text"]
        try:
            self.exporter.export_entity(entity_name, export_label=self.export_label)
            messagebox.showinfo("Information", f"Your model {entity_name} was exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.progressbar.pack_forget()
            self.export_label.pack_forget()
            self.export_btn.pack(pady=10)
            self.progressbar.stop()

    def run(self):
        self.show_entities()
        self.root.mainloop()