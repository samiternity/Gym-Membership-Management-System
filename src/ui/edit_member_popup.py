class EditMemberPopup(ctk.CTkToplevel):
    def __init__(self, parent_ui, member_id):
        super().__init__()
        self.parent_ui = parent_ui
        self.data_manager = parent_ui.data_manager
        self.member_id = member_id
        self.member = self.data_manager.get_member(member_id)
        
        self.title("Edit Member Details")
        self.geometry("400x300")
        
        self.setup_ui()
        self.grab_set()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text="First Name:").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.fname_entry = ctk.CTkEntry(self)
        self.fname_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")
        self.fname_entry.insert(0, self.member['first_name'])
        
        ctk.CTkLabel(self, text="Last Name:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.lname_entry = ctk.CTkEntry(self)
        self.lname_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        self.lname_entry.insert(0, self.member['last_name'])
        
        ctk.CTkLabel(self, text="Contact:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.contact_entry = ctk.CTkEntry(self)
        self.contact_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        self.contact_entry.insert(0, self.member['contact'])
        
        self.save_btn = ctk.CTkButton(self, text="Save Changes", command=self.save_changes)
        self.save_btn.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

    def save_changes(self):
        self.member['first_name'] = self.fname_entry.get()
        self.member['last_name'] = self.lname_entry.get()
        self.member['contact'] = self.contact_entry.get()
        
        self.data_manager.save_data("members.json")
        self.parent_ui.populate_table()
        self.destroy()
