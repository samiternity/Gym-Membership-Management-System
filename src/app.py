import customtkinter as ctk
from .data_manager import DataManager
from .backup_manager import BackupManager
from .styles import *
from PIL import Image
import os
import sys

class App(ctk.CTk):
    def __init__(self, auth_manager):
        super().__init__()
        
        self.auth_manager = auth_manager
        self.current_user = auth_manager.get_current_user()

        self.title("Gymiternity - Management System")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(True, True)

        # Data Manager
        self.data_manager = DataManager()
        
        # Backup Manager
        self.backup_manager = BackupManager()

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=SIDEBAR_WIDTH, corner_radius=0, fg_color=SIDEBAR_COLOR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) # Push logout/exit to bottom (spacer row)

        # Logo header frame
        logo_header_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_header_frame.grid(row=0, column=0, padx=10, pady=(15, 5), sticky="ew")
        
        # Logo image
        try:
            logo_path = self.get_resource_path("pics/transparent_icon.png")
            logo_image = Image.open(logo_path)
            logo_ctk = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(40, 40))
            logo_img_label = ctk.CTkLabel(logo_header_frame, image=logo_ctk, text="")
            logo_img_label.pack(side="left", padx=(5, 10))
        except Exception as e:
            print(f"Could not load sidebar logo: {e}")
        
        self.logo_label = ctk.CTkLabel(logo_header_frame, text="Gymiternity", font=ctk.CTkFont(size=18, weight="bold"))
        self.logo_label.pack(side="left")
        
        # User info label
        user_text = f"{self.current_user['username']}" if self.current_user else "User"
        self.user_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text=user_text, 
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY_COLOR
        )
        self.user_label.grid(row=0, column=0, padx=20, pady=(50, 0), sticky="s")

        self.create_sidebar_button("Dashboard", self.show_dashboard, 1)
        self.create_sidebar_button("Members", self.show_members, 2)
        self.create_sidebar_button("Trainers", self.show_trainers, 3)
        self.create_sidebar_button("Payments", self.show_payments, 4)
        self.create_sidebar_button("Attendance", self.show_attendance, 5)
        self.create_sidebar_button("Visitors", self.show_visitors, 6)
        self.create_sidebar_button("Settings", self.show_settings, 7)
        
        # Logout button at bottom
        self.logout_btn = ctk.CTkButton(
            self.sidebar_frame, 
            text="Logout", 
            command=self.logout,
            fg_color=DANGER_COLOR,
            hover_color="#c0392b",
            anchor="center"
        )
        self.logout_btn.grid(row=9, column=0, padx=20, pady=(10, 20), sticky="ew")

        # Content Frame
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=CONTENT_COLOR)
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # Initialize with Dashboard
        self.show_dashboard()
        
        # Configure global Treeview style
        self.configure_styles()
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Set window icons after window is fully created
        self.after(100, self._set_window_icons)

    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and PyInstaller."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), relative_path)

    def _set_window_icons(self):
        """Sets the window icons for title bar and taskbar."""
        try:
            # Use ICO file for Windows compatibility
            icon_path = self.get_resource_path("pics/transparent_icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
            else:
                # Fallback to PNG with iconphoto
                title_icon_path = self.get_resource_path("pics/transparent_icon.png")
                title_icon = Image.open(title_icon_path)
                title_icon = title_icon.resize((32, 32), Image.LANCZOS)
                from PIL import ImageTk
                self._title_icon = ImageTk.PhotoImage(title_icon)
                self.wm_iconphoto(True, self._title_icon)
        except Exception as e:
            print(f"Could not set window icons: {e}")

    def configure_styles(self):
        """Configures global styles for widgets like Treeview."""
        from tkinter import ttk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background=CONTENT_COLOR, 
                        foreground=TEXT_COLOR, 
                        fieldbackground=CONTENT_COLOR,
                        rowheight=30,
                        borderwidth=0)
        style.map('Treeview', background=[('selected', PRIMARY_COLOR)])
        style.configure("Treeview.Heading", 
                        background=SIDEBAR_COLOR, 
                        foreground=TEXT_COLOR, 
                        font=("Roboto", 12, "bold"))

    def create_sidebar_button(self, text, command, row):
        btn = ctk.CTkButton(self.sidebar_frame, text=text, command=command, 
                            fg_color="transparent", text_color=TEXT_SECONDARY_COLOR, 
                            hover_color=PRIMARY_COLOR, anchor="w")
        btn.grid(row=row, column=0, padx=20, pady=10, sticky="ew")

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content_frame()
        from .ui.dashboard import Dashboard
        Dashboard(self.content_frame, self.data_manager)

    def show_members(self):
        self.clear_content_frame()
        from .ui.members import Members
        Members(self.content_frame, self.data_manager)

    def show_trainers(self):
        self.clear_content_frame()
        from .ui.trainers import Trainers
        Trainers(self.content_frame, self.data_manager)

    def show_payments(self):
        self.clear_content_frame()
        from .ui.payments import Payments
        Payments(self.content_frame, self.data_manager)

    def show_attendance(self):
        self.clear_content_frame()
        from .ui.attendance import Attendance
        Attendance(self.content_frame, self.data_manager)

    def show_visitors(self):
        self.clear_content_frame()
        from .ui.visitors import Visitors
        Visitors(self.content_frame, self.data_manager)
    
    def show_settings(self):
        self.clear_content_frame()
        from .ui.settings import Settings
        Settings(self.content_frame, self.data_manager, self.backup_manager, self.auth_manager)
    
    def logout(self):
        """Logs out the current user and closes the app."""
        from tkinter import messagebox
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.auth_manager.logout()
            self.on_close()
    
    def on_close(self):
        # Create auto-backup before closing
        success, backup_name, message = self.backup_manager.create_backup()
        if success:
            print(f"Auto-backup created: {backup_name}")
        
        self.data_manager.save_all_data()
        self.destroy()
