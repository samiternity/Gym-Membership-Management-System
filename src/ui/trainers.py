import customtkinter as ctk
from tkinter import ttk
from ..styles import *
from ..utils import *

class Trainers:
    def __init__(self, parent_frame, data_manager):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        
        self.setup_ui()
        self.populate_table()

    def setup_ui(self):
        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.parent_frame.grid_rowconfigure(0, weight=0)
        self.parent_frame.grid_rowconfigure(1, weight=1)

        # Controls
        self.controls_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.controls_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        self.add_btn = ctk.CTkButton(self.controls_frame, text="+ Add New Trainer", command=lambda: self.open_popup(None))
        self.add_btn.pack(side="left", padx=(0, 10))
        
        self.edit_btn = ctk.CTkButton(self.controls_frame, text="Edit Selected", command=self.edit_selected, fg_color=ACCENT_COLOR)
        self.edit_btn.pack(side="left", padx=(0, 10))
        
        self.delete_btn = ctk.CTkButton(self.controls_frame, text="Delete Trainer", command=self.delete_trainer, fg_color=DANGER_COLOR)
        self.delete_btn.pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="Search trainer...")
        self.search_entry.pack(side="right", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda event: self.populate_table(self.search_entry.get()))

        # Table
        self.table_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        columns = ("id", "first_name", "last_name", "specialization", "contact", "fee", "status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("first_name", text="First Name")
        self.tree.heading("last_name", text="Last Name")
        self.tree.heading("specialization", text="Specialization")
        self.tree.heading("contact", text="Contact")
        self.tree.heading("fee", text="Fee")
        self.tree.heading("status", text="Status")
        
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("first_name", width=100)
        self.tree.column("last_name", width=100)
        self.tree.column("specialization", width=150)
        self.tree.column("contact", width=120)
        self.tree.column("fee", width=80, anchor="e")
        self.tree.column("status", width=80, anchor="center")

        scrollbar = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def populate_table(self, filter_query=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for tid, trainer in self.data_manager.trainers_db.items():
            if filter_query:
                full_name = f"{trainer['first_name']} {trainer['last_name']}".lower()
                specialization = trainer['specialization'].lower()
                if filter_query.lower() not in full_name and filter_query.lower() not in specialization:
                    continue
                    
            self.tree.insert("", "end", values=(
                tid,
                trainer['first_name'],
                trainer['last_name'],
                trainer['specialization'],
                trainer['contact'],
                f"${trainer['fee']}",
                trainer['status']
            ))

    def open_popup(self, trainer_id):
        AddEditTrainerPopup(self, trainer_id)

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        trainer_id = self.tree.item(selected[0])['values'][0]
        self.open_popup(trainer_id)

    def delete_trainer(self):
        import tkinter as tk
        selected = self.tree.selection()
        if not selected:
            return
        trainer_id = self.tree.item(selected[0])['values'][0]
        trainer = self.data_manager.trainers_db.get(trainer_id)
        if trainer:
            confirm = tk.messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {trainer['first_name']} {trainer['last_name']}? This cannot be undone.")
            if confirm:
                del self.data_manager.trainers_db[trainer_id]
                self.data_manager.save_data("trainers.json")
                self.populate_table()

class AddEditTrainerPopup(ctk.CTkToplevel):
    def __init__(self, parent_ui, trainer_id=None):
        super().__init__()
        self.parent_ui = parent_ui
        self.data_manager = parent_ui.data_manager
        self.trainer_id = trainer_id
        
        title = "Edit Trainer" if trainer_id else "Add New Trainer"
        self.title(title)
        self.geometry("400x450")
        
        self.setup_ui()
        if trainer_id:
            self.load_data()
        self.grab_set()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        
        fields = ["First Name", "Last Name", "Specialization", "Contact", "Fee"]
        self.entries = {}
        
        for i, field in enumerate(fields):
            ctk.CTkLabel(self, text=f"{field}:").grid(row=i, column=0, padx=20, pady=10, sticky="w")
            entry = ctk.CTkEntry(self)
            entry.grid(row=i, column=1, padx=20, pady=10, sticky="ew")
            self.entries[field] = entry

        ctk.CTkLabel(self, text="Status:").grid(row=5, column=0, padx=20, pady=10, sticky="w")
        self.status_combo = ctk.CTkComboBox(self, values=["Active", "Inactive"])
        self.status_combo.grid(row=5, column=1, padx=20, pady=10, sticky="ew")
        
        self.save_btn = ctk.CTkButton(self, text="Save Trainer", command=self.save_trainer)
        self.save_btn.grid(row=6, column=0, columnspan=2, padx=20, pady=20)

    def load_data(self):
        trainer = self.data_manager.trainers_db[self.trainer_id]
        self.entries["First Name"].insert(0, trainer['first_name'])
        self.entries["Last Name"].insert(0, trainer['last_name'])
        self.entries["Specialization"].insert(0, trainer['specialization'])
        self.entries["Contact"].insert(0, trainer['contact'])
        self.entries["Fee"].insert(0, str(trainer['fee']))
        self.status_combo.set(trainer['status'])

    def save_trainer(self):
        data = {
            "first_name": self.entries["First Name"].get(),
            "last_name": self.entries["Last Name"].get(),
            "specialization": self.entries["Specialization"].get(),
            "contact": self.entries["Contact"].get(),
            "fee": float(self.entries["Fee"].get() or 0),
            "status": self.status_combo.get()
        }
        
        if self.trainer_id:
            self.data_manager.trainers_db[self.trainer_id] = data
        else:
            new_id = generate_unique_id("T")
            self.data_manager.trainers_db[new_id] = data
            
        self.data_manager.save_data("trainers.json")
        self.parent_ui.populate_table()
        self.destroy()
