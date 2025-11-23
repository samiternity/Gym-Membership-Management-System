import customtkinter as ctk
from tkinter import ttk
from ..styles import *
from ..utils import *

class Visitors:
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
        
        self.add_btn = ctk.CTkButton(self.controls_frame, text="+ Add Visitor", command=lambda: self.open_popup(None))
        self.add_btn.pack(side="left", padx=(0, 10))
        
        self.edit_btn = ctk.CTkButton(self.controls_frame, text="Edit Visitor", command=self.edit_selected, fg_color=ACCENT_COLOR)
        self.edit_btn.pack(side="left", padx=(0, 10))
        
        self.delete_btn = ctk.CTkButton(self.controls_frame, text="Delete Visitor", command=self.delete_visitor, fg_color=DANGER_COLOR)
        self.delete_btn.pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="Search visitor...")
        self.search_entry.pack(side="right", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda event: self.populate_table(self.search_entry.get()))

        # Table
        self.table_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        columns = ("id", "first_name", "last_name", "contact", "visit_date", "interested_in", "status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("first_name", text="First Name")
        self.tree.heading("last_name", text="Last Name")
        self.tree.heading("contact", text="Contact")
        self.tree.heading("visit_date", text="Visit Date")
        self.tree.heading("interested_in", text="Interested In")
        self.tree.heading("status", text="Status")
        
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("first_name", width=100)
        self.tree.column("last_name", width=100)
        self.tree.column("contact", width=120)
        self.tree.column("visit_date", width=100, anchor="center")
        self.tree.column("interested_in", width=150)
        self.tree.column("status", width=100, anchor="center")

        scrollbar = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def populate_table(self, filter_query=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for visitor in self.data_manager.visitors_log:
            if filter_query:
                full_name = f"{visitor['first_name']} {visitor['last_name']}".lower()
                if filter_query.lower() not in full_name:
                    continue
                    
            self.tree.insert("", "end", values=(
                visitor['visitor_id'],
                visitor['first_name'],
                visitor['last_name'],
                visitor['contact'],
                visitor['visit_date'],
                visitor['interested_in'],
                visitor['status']
            ))

    def open_popup(self, visitor_id):
        AddEditVisitorPopup(self, visitor_id)

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        visitor_id = self.tree.item(selected[0])['values'][0]
        self.open_popup(visitor_id)

    def delete_visitor(self):
        import tkinter as tk
        selected = self.tree.selection()
        if not selected:
            return
        visitor_id = self.tree.item(selected[0])['values'][0]
        visitor = next((v for v in self.data_manager.visitors_log if v['visitor_id'] == visitor_id), None)
        if visitor:
            confirm = tk.messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {visitor['first_name']} {visitor['last_name']}? This cannot be undone.")
            if confirm:
                self.data_manager.visitors_log.remove(visitor)
                self.data_manager.save_data("visitors_log.json")
                self.populate_table()

class AddEditVisitorPopup(ctk.CTkToplevel):
    def __init__(self, parent_ui, visitor_id=None):
        super().__init__()
        self.parent_ui = parent_ui
        self.data_manager = parent_ui.data_manager
        self.visitor_id = visitor_id
        
        title = "Edit Visitor" if visitor_id else "Add New Visitor"
        self.title(title)
        self.geometry("400x450")
        
        self.setup_ui()
        if visitor_id:
            self.load_data()
        self.grab_set()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        
        fields = ["First Name", "Last Name", "Contact", "Interested In"]
        self.entries = {}
        
        for i, field in enumerate(fields):
            ctk.CTkLabel(self, text=f"{field}:").grid(row=i, column=0, padx=20, pady=10, sticky="w")
            entry = ctk.CTkEntry(self)
            entry.grid(row=i, column=1, padx=20, pady=10, sticky="ew")
            self.entries[field] = entry

        ctk.CTkLabel(self, text="Status:").grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.status_combo = ctk.CTkComboBox(self, values=["Follow-up", "Joined", "Not Interested"])
        self.status_combo.grid(row=4, column=1, padx=20, pady=10, sticky="ew")
        
        self.save_btn = ctk.CTkButton(self, text="Save Visitor", command=self.save_visitor)
        self.save_btn.grid(row=5, column=0, columnspan=2, padx=20, pady=20)

    def load_data(self):
        visitor = next((v for v in self.data_manager.visitors_log if v['visitor_id'] == self.visitor_id), None)
        if visitor:
            self.entries["First Name"].insert(0, visitor['first_name'])
            self.entries["Last Name"].insert(0, visitor['last_name'])
            self.entries["Contact"].insert(0, visitor['contact'])
            self.entries["Interested In"].insert(0, visitor['interested_in'])
            self.status_combo.set(visitor['status'])

    def save_visitor(self):
        data = {
            "first_name": self.entries["First Name"].get(),
            "last_name": self.entries["Last Name"].get(),
            "contact": self.entries["Contact"].get(),
            "interested_in": self.entries["Interested In"].get(),
            "status": self.status_combo.get(),
            "visit_date": get_current_date_iso() # Update date on edit? Or keep original? Let's keep simple.
        }
        
        if self.visitor_id:
            # Update existing
            for v in self.data_manager.visitors_log:
                if v['visitor_id'] == self.visitor_id:
                    v.update(data)
                    break
        else:
            data["visitor_id"] = generate_unique_id("V")
            self.data_manager.visitors_log.append(data)
            
        self.data_manager.save_data("visitors_log.json")
        self.parent_ui.populate_table()
        self.destroy()
