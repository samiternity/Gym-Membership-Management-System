import customtkinter as ctk
from tkinter import ttk, messagebox
from ..styles import *
from datetime import datetime

class Settings:
    """Settings module for backup management and system configuration."""
    
    def __init__(self, parent_frame, data_manager, backup_manager, auth_manager):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        self.backup_manager = backup_manager
        self.auth_manager = auth_manager
        
        self.setup_ui()
        self.load_backups()
    
    def setup_ui(self):
        """Sets up the settings UI."""
        # Grid configuration
        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.parent_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")
        
        # Main content with tabs
        self.tabview = ctk.CTkTabview(self.parent_frame)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Create tabs
        self.tabview.add("Backup & Restore")
        self.tabview.add("Account")
        
        # Build tab contents
        self.build_backup_tab()
        self.build_account_tab()
    
    def build_backup_tab(self):
        """Builds the backup and restore tab."""
        tab = self.tabview.tab("Backup & Restore")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Controls frame
        controls_frame = ctk.CTkFrame(tab, fg_color=SIDEBAR_COLOR)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Create backup button
        create_backup_btn = ctk.CTkButton(
            controls_frame,
            text="Create Backup",
            command=self.create_backup,
            fg_color=PRIMARY_COLOR,
            hover_color=ACCENT_COLOR,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        create_backup_btn.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="Refresh",
            command=self.load_backups,
            fg_color="transparent",
            border_width=2,
            border_color=PRIMARY_COLOR,
            height=40
        )
        refresh_btn.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        # Info label
        info_label = ctk.CTkLabel(
            controls_frame,
            text="Backups are automatically created when you close the app. Last 7 backups are kept.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY_COLOR
        )
        info_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")
        
        # Backups list frame
        list_frame = ctk.CTkFrame(tab, fg_color=SIDEBAR_COLOR)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Table
        columns = ("Name", "Date", "Size (KB)", "Files")
        self.backup_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.backup_tree.heading("Name", text="Backup Name")
        self.backup_tree.heading("Date", text="Date Created")
        self.backup_tree.heading("Size (KB)", text="Size (KB)")
        self.backup_tree.heading("Files", text="Files")
        
        self.backup_tree.column("Name", width=250)
        self.backup_tree.column("Date", width=180)
        self.backup_tree.column("Size (KB)", width=100)
        self.backup_tree.column("Files", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        self.backup_tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=10)
        
        # Action buttons frame
        action_frame = ctk.CTkFrame(tab, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        restore_btn = ctk.CTkButton(
            action_frame,
            text="Restore Selected",
            command=self.restore_backup,
            fg_color=SUCCESS_COLOR,
            hover_color="#27ae60",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        restore_btn.pack(side="left", padx=5)
        
        validate_btn = ctk.CTkButton(
            action_frame,
            text="Validate Selected",
            command=self.validate_backup,
            fg_color="transparent",
            border_width=2,
            border_color=SUCCESS_COLOR,
            height=40
        )
        validate_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            action_frame,
            text="Delete Selected",
            command=self.delete_backup,
            fg_color=DANGER_COLOR,
            hover_color="#c0392b",
            height=40
        )
        delete_btn.pack(side="right", padx=5)
    
    def build_account_tab(self):
        """Builds the account settings tab."""
        tab = self.tabview.tab("Account")
        tab.grid_columnconfigure(0, weight=1)
        
        # Account info frame
        info_frame = ctk.CTkFrame(tab, fg_color=SIDEBAR_COLOR)
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        current_user = self.auth_manager.get_current_user()
        
        # User info
        user_label = ctk.CTkLabel(
            info_frame,
            text=f"Logged in as: {current_user['username']}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        user_label.pack(pady=(20, 10), padx=20, anchor="w")
        
        role_label = ctk.CTkLabel(
            info_frame,
            text=f"Role: {current_user['role']}",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_SECONDARY_COLOR
        )
        role_label.pack(pady=(0, 20), padx=20, anchor="w")
        
        # Change password frame
        password_frame = ctk.CTkFrame(tab, fg_color=SIDEBAR_COLOR)
        password_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        password_title = ctk.CTkLabel(
            password_frame,
            text="Change Password",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        password_title.pack(pady=(20, 10), padx=20, anchor="w")
        
        # New password entry
        new_password_label = ctk.CTkLabel(
            password_frame,
            text="New Password:",
            font=ctk.CTkFont(size=12)
        )
        new_password_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.new_password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Enter new password",
            show="●",
            height=35
        )
        self.new_password_entry.pack(pady=(0, 10), padx=20, fill="x")
        
        # Confirm password entry
        confirm_password_label = ctk.CTkLabel(
            password_frame,
            text="Confirm Password:",
            font=ctk.CTkFont(size=12)
        )
        confirm_password_label.pack(pady=(0, 5), padx=20, anchor="w")
        
        self.confirm_password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Confirm new password",
            show="●",
            height=35
        )
        self.confirm_password_entry.pack(pady=(0, 20), padx=20, fill="x")
        
        # Change password button
        change_password_btn = ctk.CTkButton(
            password_frame,
            text="Change Password",
            command=self.change_password,
            fg_color=PRIMARY_COLOR,
            hover_color=ACCENT_COLOR,
            height=40
        )
        change_password_btn.pack(pady=(0, 20), padx=20, fill="x")
    
    def load_backups(self):
        """Loads and displays available backups."""
        # Clear existing items
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
        
        # Get backups
        backups = self.backup_manager.list_backups()
        
        # Populate table
        for backup in backups:
            self.backup_tree.insert("", "end", values=(
                backup['name'],
                backup['date'],
                backup['size_kb'],
                backup['file_count']
            ))
    
    def create_backup(self):
        """Creates a new backup."""
        success, backup_name, message = self.backup_manager.create_backup()
        
        if success:
            messagebox.showinfo("Backup Created", message)
            self.load_backups()
        else:
            messagebox.showerror("Backup Failed", message)
    
    def restore_backup(self):
        """Restores from selected backup."""
        selection = self.backup_tree.selection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select a backup to restore")
            return
        
        # Get backup name
        item = self.backup_tree.item(selection[0])
        backup_name = item['values'][0]
        
        # Confirm
        if not messagebox.askyesno(
            "Confirm Restore",
            f"Are you sure you want to restore from '{backup_name}'?\n\n"
            "This will replace all current data with the backup data."
        ):
            return
        
        # Restore
        success, message = self.backup_manager.restore_backup(backup_name)
        
        if success:
            # Reload all data from restored files
            self.data_manager.load_all_data()
            messagebox.showinfo("Restore Successful", 
                f"{message}\n\nData has been reloaded. Please refresh your current view.")
        else:
            messagebox.showerror("Restore Failed", message)
    
    def validate_backup(self):
        """Validates selected backup."""
        selection = self.backup_tree.selection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select a backup to validate")
            return
        
        # Get backup name
        item = self.backup_tree.item(selection[0])
        backup_name = item['values'][0]
        
        # Validate
        valid, message = self.backup_manager.validate_backup(backup_name)
        
        if valid:
            messagebox.showinfo("Validation Successful", message)
        else:
            messagebox.showerror("Validation Failed", message)
    
    def delete_backup(self):
        """Deletes selected backup."""
        selection = self.backup_tree.selection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select a backup to delete")
            return
        
        # Get backup name
        item = self.backup_tree.item(selection[0])
        backup_name = item['values'][0]
        
        # Confirm
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{backup_name}'?"
        ):
            return
        
        # Delete
        success, message = self.backup_manager.delete_backup(backup_name)
        
        if success:
            messagebox.showinfo("Delete Successful", message)
            self.load_backups()
        else:
            messagebox.showerror("Delete Failed", message)
    
    def change_password(self):
        """Changes the current user's password."""
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validate
        if not new_password:
            messagebox.showwarning("Invalid Input", "Please enter a new password")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Password Mismatch", "Passwords do not match")
            return
        
        if len(new_password) < 4:
            messagebox.showwarning("Weak Password", "Password must be at least 4 characters")
            return
        
        # Change password
        current_user = self.auth_manager.get_current_user()
        success, message = self.auth_manager.change_password(current_user['username'], new_password)
        
        if success:
            messagebox.showinfo("Success", message)
            self.new_password_entry.delete(0, 'end')
            self.confirm_password_entry.delete(0, 'end')
        else:
            messagebox.showerror("Error", message)
