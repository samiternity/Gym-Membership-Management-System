import customtkinter as ctk
from tkinter import ttk
from ..styles import *
from ..utils import *

class Payments:
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
        
        self.unpaid_var = ctk.BooleanVar(value=True)
        self.unpaid_chk = ctk.CTkCheckBox(self.controls_frame, text="Show Unpaid Members Only", 
                                          variable=self.unpaid_var, command=self.populate_table)
        self.unpaid_chk.pack(side="left", padx=(0, 20))
        
        self.pay_btn = ctk.CTkButton(self.controls_frame, text="Mark Selected as Paid", 
                                     command=self.mark_as_paid, fg_color=SUCCESS_COLOR)
        self.pay_btn.pack(side="left", padx=(0, 10))
        
        self.unpay_btn = ctk.CTkButton(self.controls_frame, text="Mark as Unpaid", 
                                     command=self.mark_as_unpaid, fg_color=DANGER_COLOR)
        self.unpay_btn.pack(side="left", padx=(0, 10))

        self.edit_btn = ctk.CTkButton(self.controls_frame, text="Edit Amount", 
                                     command=self.edit_amount, fg_color=ACCENT_COLOR)
        self.edit_btn.pack(side="left", padx=(0, 10))
        
        # WhatsApp reminder button
        self.whatsapp_btn = ctk.CTkButton(
            self.controls_frame, 
            text="Send WhatsApp Reminder", 
            command=self.send_whatsapp_reminder,
            fg_color="#25D366",
            hover_color="#128C7E"
        )
        self.whatsapp_btn.pack(side="left")

        # Table
        self.table_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        columns = ("id", "member", "amount", "due_date", "status", "paid_date")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="Payment ID")
        self.tree.heading("member", text="Member Name")
        self.tree.heading("amount", text="Amount Due")
        self.tree.heading("due_date", text="Due Date")
        self.tree.heading("status", text="Status")
        self.tree.heading("paid_date", text="Paid Date")
        
        self.tree.column("id", width=100, anchor="center")
        self.tree.column("member", width=150)
        self.tree.column("amount", width=100, anchor="e")
        self.tree.column("due_date", width=100, anchor="center")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("paid_date", width=100, anchor="center")
        
        # Tags for coloring
        self.tree.tag_configure("Unpaid", foreground=DANGER_COLOR)
        self.tree.tag_configure("Paid", foreground=SUCCESS_COLOR)

        scrollbar = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def populate_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        show_unpaid_only = self.unpaid_var.get()
        
        # Sort payments: Unpaid first (by due_date asc), then Paid (by payment_date desc)
        payments_to_display = []
        for payment in self.data_manager.payments_log:
            if show_unpaid_only and payment['status'] != 'Unpaid':
                continue
            payments_to_display.append(payment)
        
        # Sort: Unpaid payments first (earliest due date first), then Paid payments (most recent payment first)
        unpaid_payments = [p for p in payments_to_display if p['status'] == 'Unpaid']
        paid_payments = [p for p in payments_to_display if p['status'] == 'Paid']
        
        unpaid_payments.sort(key=lambda x: x['due_date'])
        paid_payments.sort(key=lambda x: x.get('payment_date') or '', reverse=True)
        
        sorted_payments = unpaid_payments + paid_payments
        
        for payment in sorted_payments:
            member = self.data_manager.get_member(payment['member_id'])
            member_name = f"{member['first_name']} {member['last_name']}" if member else "Unknown"
            
            self.tree.insert("", "end", values=(
                payment['payment_id'],
                member_name,
                f"${payment['amount_due']}",
                payment['due_date'],
                payment['status'],
                payment['payment_date'] or "-"
            ), tags=(payment['status'],))

    def mark_as_paid(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        payment_id = self.tree.item(selected[0])['values'][0]
        
        # Find payment
        for payment in self.data_manager.payments_log:
            if payment['payment_id'] == payment_id:
                if payment['status'] == 'Paid':
                    return # Already paid
                    
                payment['status'] = 'Paid'
                payment['amount_paid'] = payment['amount_due']
                payment['payment_date'] = get_current_datetime_iso()
                break
        
        self.data_manager.save_data("payments_log.json")
        self.data_manager.save_data("payments_log.json")
        self.populate_table()

    def mark_as_unpaid(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        payment_id = self.tree.item(selected[0])['values'][0]
        
        # Find payment
        for payment in self.data_manager.payments_log:
            if payment['payment_id'] == payment_id:
                if payment['status'] == 'Unpaid':
                    return # Already unpaid
                    
                payment['status'] = 'Unpaid'
                payment['amount_paid'] = 0.0
                payment['payment_date'] = None
                break
        
        self.data_manager.save_data("payments_log.json")
        self.populate_table()

    def edit_amount(self):
        import tkinter as tk
        selected = self.tree.selection()
        if not selected:
            return
            
        payment_id = self.tree.item(selected[0])['values'][0]
        
        # Find payment
        target_payment = None
        for payment in self.data_manager.payments_log:
            if payment['payment_id'] == payment_id:
                target_payment = payment
                break
        
        if not target_payment:
            return

        # Simple input dialog
        dialog = ctk.CTkInputDialog(text="Enter new amount due:", title="Edit Amount")
        new_amount_str = dialog.get_input()
        
        if new_amount_str:
            try:
                new_amount = float(new_amount_str)
                target_payment['amount_due'] = new_amount
                if target_payment['status'] == 'Paid':
                    target_payment['amount_paid'] = new_amount # Update paid amount if already paid
                
                self.data_manager.save_data("payments_log.json")
                self.populate_table()
            except ValueError:
                tk.messagebox.showerror("Invalid Input", "Please enter a valid number.")
    
    def send_whatsapp_reminder(self):
        """Sends WhatsApp payment reminder to selected member."""
        import tkinter as tk
        from ..whatsapp_helper import open_whatsapp_chat, get_payment_reminder_message
        
        selected = self.tree.selection()
        if not selected:
            tk.messagebox.showwarning("No Selection", "Please select a payment to send reminder")
            return
        
        # Get payment details
        payment_id = self.tree.item(selected[0])['values'][0]
        
        # Find payment
        payment = None
        for p in self.data_manager.payments_log:
            if p['payment_id'] == payment_id:
                payment = p
                break
        
        if not payment:
            return
        
        # Check if already paid
        if payment['status'] == 'Paid':
            tk.messagebox.showinfo("Already Paid", "This payment has already been marked as paid")
            return
        
        # Get member info
        member = self.data_manager.get_member(payment['member_id'])
        if not member:
            tk.messagebox.showerror("Error", "Member not found")
            return
        
        # Check if member has contact
        contact = member.get('contact', '')
        if not contact:
            tk.messagebox.showwarning("No Contact", "This member has no contact number on file")
            return
        
        # Generate reminder message
        member_name = f"{member['first_name']} {member['last_name']}"
        amount = payment['amount_due']
        due_date = payment['due_date']
        
        message = get_payment_reminder_message(member_name, amount, due_date)
        
        # Open WhatsApp
        success, result_message = open_whatsapp_chat(contact, message)
        if not success:
            tk.messagebox.showerror("WhatsApp Error", result_message)
