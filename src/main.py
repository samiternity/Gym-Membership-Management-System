import customtkinter as ctk
from src.app import App
from src.auth_manager import AuthManager
from src.ui.login import show_login_dialog

if __name__ == "__main__":
    # Set appearance mode
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create auth manager
    auth_manager = AuthManager()
    
    while True:
        # Create a temporary root window for login
        temp_root = ctk.CTk()
        temp_root.withdraw()  # Hide the window
        
        # Show login dialog
        login_success = show_login_dialog(temp_root, auth_manager)
        
        # Destroy temp window
        temp_root.destroy()
        
        if login_success:
            # Create and run main app
            app = App(auth_manager)
            app.mainloop()
            
            # After app closes, check if we should exit or loop back
            # If user logged out, auth_manager.current_user will be None
            if auth_manager.is_logged_in():
                # If still logged in (e.g. closed window), exit
                break
            else:
                # If logged out, loop continues to show login screen again
                print("User logged out, returning to login screen...")
                pass
        else:
            # User cancelled login
            print("Login cancelled")
            break
