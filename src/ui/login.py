import customtkinter as ctk
from tkinter import messagebox
from ..auth_manager import AuthManager
from ..styles import *

class LoginWindow(ctk.CTkToplevel):
    """Login window displayed before main application."""
    
    def __init__(self, parent, auth_manager):
        super().__init__(parent)
        
        self.parent = parent
        self.auth_manager = auth_manager
        self.login_successful = False
        
        self.title("Gym Manager - Login")
        self.geometry("400x600")
        self.resizable(False, False)
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.setup_ui()
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Focus on username field
        self.username_entry.focus()
        
        # Bind Enter key to login
        self.bind('<Return>', lambda e: self.attempt_login())
    
    def setup_ui(self):
        """Sets up the login UI."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=CONTENT_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🏋️ Gym Manager",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        title_label.pack(pady=(40, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Membership Management System",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_SECONDARY_COLOR
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Login form container
        form_frame = ctk.CTkFrame(main_frame, fg_color=SIDEBAR_COLOR)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Username
        username_label = ctk.CTkLabel(
            form_frame,
            text="Username",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        username_label.pack(pady=(30, 5), padx=20, fill="x")
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter username",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.username_entry.pack(pady=(0, 20), padx=20, fill="x")
        
        # Password
        password_label = ctk.CTkLabel(
            form_frame,
            text="Password",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        password_label.pack(pady=(0, 5), padx=20, fill="x")
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter password",
            show="●",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.password_entry.pack(pady=(0, 30), padx=20, fill="x")
        
        # Error message label (hidden by default)
        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=DANGER_COLOR
        )
        self.error_label.pack(pady=(0, 10), padx=20)

        # Login button
        self.login_button = ctk.CTkButton(
            form_frame,
            text="Login",
            command=self.attempt_login,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=ACCENT_COLOR
        )
        self.login_button.pack(pady=(0, 10), padx=20, fill="x")
        
        # Forgot Password
        forgot_btn = ctk.CTkButton(
            form_frame,
            text="Forgot Password?",
            command=self.forgot_password,
            fg_color="transparent",
            text_color=TEXT_SECONDARY_COLOR,
            hover_color=SIDEBAR_COLOR,
            font=ctk.CTkFont(size=12, underline=True),
            height=20
        )
        forgot_btn.pack(pady=(0, 20))
        
        # Default credentials hint
        hint_label = ctk.CTkLabel(
            form_frame,
            text="Default: admin / admin123",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY_COLOR
        )
        hint_label.pack(pady=(0, 20))

    def forgot_password(self):
        """Shows forgot password message."""
        messagebox.showinfo("Forgot Password", "Please contact the system administrator to reset your password.\n\nFor this local version, you can check 'users.json' in the data folder.")
    
    def attempt_login(self):
        """Attempts to log in with entered credentials."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Clear previous error
        self.error_label.configure(text="")
        
        # Validate input
        if not username:
            self.show_error("Please enter username")
            self.username_entry.focus()
            return
        
        if not password:
            self.show_error("Please enter password")
            self.password_entry.focus()
            return
        
        # Attempt login
        success, user_data, message = self.auth_manager.login(username, password)
        
        if success:
            self.login_successful = True
            self.grab_release()
            self.destroy()
        else:
            self.show_error(message)
            self.password_entry.delete(0, 'end')
            self.password_entry.focus()
    
    def show_error(self, message):
        """Displays an error message."""
        self.error_label.configure(text=message)
    
    def get_result(self):
        """Returns whether login was successful."""
        return self.login_successful


def show_login_dialog(parent, auth_manager):
    """Shows login dialog and returns success status.
    
    Args:
        parent: Parent window
        auth_manager: AuthManager instance
        
    Returns:
        bool: True if login successful, False otherwise
    """
    dialog = LoginWindow(parent, auth_manager)
    parent.wait_window(dialog)
    return dialog.get_result()
