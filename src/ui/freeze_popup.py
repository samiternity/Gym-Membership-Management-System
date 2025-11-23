import customtkinter as ctk
import tkinter as tk
from ..styles import *
from ..freeze_manager import FreezeManager
from ..utils import get_current_date_iso
from datetime import datetime, timedelta

class FreezeMembershipPopup(ctk.CTkToplevel):
    """Popup for freezing a membership."""
    
    def __init__(self, parent, membership):
        super().__init__(parent)
        
        self.parent = parent
        self.data_manager = parent.data_manager
        self.membership = membership
        self.freeze_manager = FreezeManager(self.data_manager)
        
        self.title("Freeze Membership")
        self.geometry("450x400")
        
        self.setup_ui()
        self.grab_set()
    
    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Freeze Membership",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))
        
        # Info
        info_label = ctk.CTkLabel(
            self,
            text=f"Membership ID: {self.membership['membership_id']}",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY_COLOR
        )
        info_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Freeze Start Date
        ctk.CTkLabel(self, text="Freeze Start Date:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.start_entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD")
        self.start_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        self.start_entry.insert(0, get_current_date_iso())
        
        # Freeze End Date
        ctk.CTkLabel(self, text="Freeze End Date:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.end_entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD")
        self.end_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        
        # Suggested end date (30 days from now)
        suggested_end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.end_entry.insert(0, suggested_end)
        
        # Reason
        ctk.CTkLabel(self, text="Reason:").grid(row=4, column=0, padx=20, pady=10, sticky="nw")
        self.reason_entry = ctk.CTkTextbox(self, height=80)
        self.reason_entry.grid(row=4, column=1, padx=20, pady=10, sticky="ew")
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="gray",
            width=100
        )
        cancel_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Freeze Membership",
            command=self.freeze_membership,
            fg_color=ACCENT_COLOR,
            width=150
        )
        save_btn.pack(side="left", padx=5)
    
    def freeze_membership(self):
        """Processes the freeze request."""
        start_date = self.start_entry.get().strip()
        end_date = self.end_entry.get().strip()
        reason = self.reason_entry.get("1.0", "end-1c").strip()
        
        # Validate
        if not start_date or not end_date:
            tk.messagebox.showerror("Validation Error", "Please enter both start and end dates")
            return
        
        if not reason:
            tk.messagebox.showerror("Validation Error", "Please provide a reason for freezing")
            return
        
        # Validate date format
        try:
            datetime.fromisoformat(start_date)
            datetime.fromisoformat(end_date)
        except ValueError:
            tk.messagebox.showerror("Invalid Date", "Please use YYYY-MM-DD format for dates")
            return
        
        # Get current user (approved_by)
        approved_by = "admin"  # Default, could get from auth_manager
        
        # Add freeze
        success, message = self.freeze_manager.add_freeze(
            self.membership['membership_id'],
            start_date,
            end_date,
            reason,
            approved_by
        )
        
        if success:
            tk.messagebox.showinfo("Success", message)
            # Refresh parent if it has a method to rebuild
            if hasattr(self.parent, 'build_membership_tab'):
                try:
                    # Clear and rebuild the tab
                    for widget in self.parent.tabview.tab("Membership History").winfo_children():
                        widget.destroy()
                    self.parent.build_membership_tab()
                except:
                    pass
            self.destroy()
        else:
            tk.messagebox.showerror("Error", message)
