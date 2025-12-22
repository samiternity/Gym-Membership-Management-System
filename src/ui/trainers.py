import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from ..styles import *
from ..utils import *
import re

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
        
        self.view_profile_btn = ctk.CTkButton(self.controls_frame, text="View Profile", command=self.view_trainer_profile, fg_color=SUCCESS_COLOR)
        self.view_profile_btn.pack(side="left", padx=(0, 10))
        
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

    def view_trainer_profile(self):
        selected = self.tree.selection()
        if not selected:
            tk.messagebox.showwarning("No Selection", "Please select a trainer to view their profile")
            return
        trainer_id = self.tree.item(selected[0])['values'][0]
        TrainerProfilePopup(self, trainer_id)

    def delete_trainer(self):
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


class TrainerProfilePopup(ctk.CTkToplevel):
    """Popup to view trainer profile and assigned members."""
    def __init__(self, parent_ui, trainer_id):
        super().__init__()
        self.parent_ui = parent_ui
        self.data_manager = parent_ui.data_manager
        self.trainer_id = trainer_id
        self.trainer = self.data_manager.trainers_db.get(trainer_id)
        
        self.title(f"Trainer Profile - {self.trainer['first_name']} {self.trainer['last_name']}")
        self.geometry("600x500")
        
        self.setup_ui()
        self.grab_set()
    
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Trainer Info Section
        info_frame = ctk.CTkFrame(self, fg_color=SIDEBAR_COLOR)
        info_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(info_frame, text=f"{self.trainer['first_name']} {self.trainer['last_name']}", 
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(15, 5), padx=20, anchor="w")
        ctk.CTkLabel(info_frame, text=f"Specialization: {self.trainer['specialization']}", 
                     text_color=TEXT_SECONDARY_COLOR).pack(pady=2, padx=20, anchor="w")
        ctk.CTkLabel(info_frame, text=f"Contact: {self.trainer['contact']}", 
                     text_color=TEXT_SECONDARY_COLOR).pack(pady=2, padx=20, anchor="w")
        ctk.CTkLabel(info_frame, text=f"Fee: ${self.trainer['fee']}  |  Status: {self.trainer['status']}", 
                     text_color=TEXT_SECONDARY_COLOR).pack(pady=(2, 15), padx=20, anchor="w")
        
        # Assigned Members Section
        ctk.CTkLabel(self, text="📋 Assigned Members", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=1, column=0, sticky="w", padx=20, pady=(10, 5))
        
        # Members Table
        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("member_id", "name", "plan", "status", "end_date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("member_id", text="Member ID")
        self.tree.heading("name", text="Member Name")
        self.tree.heading("plan", text="Plan")
        self.tree.heading("status", text="Status")
        self.tree.heading("end_date", text="End Date")
        
        self.tree.column("member_id", width=80)
        self.tree.column("name", width=150)
        self.tree.column("plan", width=100)
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("end_date", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Populate assigned members
        self.populate_assigned_members()
    
    def populate_assigned_members(self):
        """Find and display all members assigned to this trainer."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Find memberships with this trainer
        for membership in self.data_manager.membership_history:
            if membership.get('assigned_trainer_id') == self.trainer_id:
                member = self.data_manager.get_member(membership['member_id'])
                plan = self.data_manager.get_plan(membership['plan_id'])
                
                if member:
                    member_name = f"{member['first_name']} {member['last_name']}"
                    plan_name = plan['name'] if plan else "Unknown"
                    
                    self.tree.insert("", "end", values=(
                        membership['member_id'],
                        member_name,
                        plan_name,
                        membership['status'],
                        membership['end_date']
                    ))


class AddEditTrainerPopup(ctk.CTkToplevel):
    def __init__(self, parent_ui, trainer_id=None):
        super().__init__()
        self.parent_ui = parent_ui
        self.data_manager = parent_ui.data_manager
        self.trainer_id = trainer_id
        
        title = "Edit Trainer" if trainer_id else "Add New Trainer"
        self.title(title)
        self.geometry("400x500")
        
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
        
        # Validation hints
        hints_text = "• First Name, Last Name, Specialization are required\n• Contact: optional, 11 digits if provided\n• Fee: must be a positive number"
        hints_label = ctk.CTkLabel(self, text=hints_text, font=ctk.CTkFont(size=11), 
                                   text_color=TEXT_SECONDARY_COLOR, justify="left")
        hints_label.grid(row=6, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")
        
        self.save_btn = ctk.CTkButton(self, text="Save Trainer", command=self.save_trainer)
        self.save_btn.grid(row=7, column=0, columnspan=2, padx=20, pady=20)

    def load_data(self):
        trainer = self.data_manager.trainers_db[self.trainer_id]
        self.entries["First Name"].insert(0, trainer['first_name'])
        self.entries["Last Name"].insert(0, trainer['last_name'])
        self.entries["Specialization"].insert(0, trainer['specialization'])
        self.entries["Contact"].insert(0, trainer['contact'])
        self.entries["Fee"].insert(0, str(trainer['fee']))
        self.status_combo.set(trainer['status'])

    def validate_input(self):
        """Validates trainer input fields."""
        errors = []
        
        # Required fields
        first_name = self.entries["First Name"].get().strip()
        last_name = self.entries["Last Name"].get().strip()
        specialization = self.entries["Specialization"].get().strip()
        contact = self.entries["Contact"].get().strip()
        fee_str = self.entries["Fee"].get().strip()
        
        if not first_name:
            errors.append("First Name is required")
        if not last_name:
            errors.append("Last Name is required")
        if not specialization:
            errors.append("Specialization is required")
        
        # Contact: optional but must be valid if provided (11 digits)
        if contact:
            if not re.match(r'^\d{11}$', contact):
                errors.append("Contact must be exactly 11 digits")
        
        # Fee: must be a positive number
        if not fee_str:
            errors.append("Fee is required")
        else:
            try:
                fee = float(fee_str)
                if fee < 0:
                    errors.append("Fee must be a positive number")
            except ValueError:
                errors.append("Fee must be a valid number")
        
        return errors

    def save_trainer(self):
        # Validate
        errors = self.validate_input()
        if errors:
            tk.messagebox.showerror("Validation Error", "\n".join(errors))
            return
        
        data = {
            "first_name": self.entries["First Name"].get().strip(),
            "last_name": self.entries["Last Name"].get().strip(),
            "specialization": self.entries["Specialization"].get().strip(),
            "contact": self.entries["Contact"].get().strip(),
            "fee": float(self.entries["Fee"].get().strip()),
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
