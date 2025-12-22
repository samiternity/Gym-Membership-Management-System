import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
import datetime
from ..styles import *
from ..utils import *

class Members:
    def __init__(self, parent_frame, data_manager):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        
        self.setup_ui()
        self.populate_table()

    def setup_ui(self):
        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.parent_frame.grid_rowconfigure(0, weight=0) # Controls
        self.parent_frame.grid_rowconfigure(1, weight=1) # Table

        # Controls Frame
        self.controls_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.controls_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        self.add_btn = ctk.CTkButton(self.controls_frame, text="+ Add New Member", command=self.open_add_member_popup)
        self.add_btn.pack(side="left", padx=(0, 10))
        
        self.edit_btn = ctk.CTkButton(self.controls_frame, text="Edit Member", command=self.open_edit_member_popup, fg_color=ACCENT_COLOR)
        self.edit_btn.pack(side="left", padx=(0, 10))
        
        self.delete_btn = ctk.CTkButton(self.controls_frame, text="Delete Member", command=self.delete_member, fg_color=DANGER_COLOR)
        self.delete_btn.pack(side="left", padx=(0, 10))
        
        self.view_btn = ctk.CTkButton(self.controls_frame, text="View Profile", command=self.open_member_profile, fg_color=ACCENT_COLOR)
        self.view_btn.pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="Search by name...")
        self.search_entry.pack(side="right", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda event: self.populate_table(self.search_entry.get()))

        # Table Frame
        self.table_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        columns = ("id", "first_name", "last_name", "contact", "plan", "trainer", "status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("first_name", text="First Name")
        self.tree.heading("last_name", text="Last Name")
        self.tree.heading("contact", text="Contact")
        self.tree.heading("plan", text="Plan")
        self.tree.heading("trainer", text="Trainer")
        self.tree.heading("status", text="Status")
        
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("first_name", width=120)
        self.tree.column("last_name", width=120)
        self.tree.column("contact", width=120)
        self.tree.column("plan", width=120)
        self.tree.column("trainer", width=120)
        self.tree.column("status", width=100, anchor="center")

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def populate_table(self, filter_query=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for member_id, member in self.data_manager.members_db.items():
            if filter_query:
                full_name = f"{member['first_name']} {member['last_name']}".lower()
                if filter_query.lower() not in full_name:
                    continue
            
            # Get Status and Details
            status = "Inactive"
            plan_name = "-"
            trainer_name = "-"
            
            # Find active membership
            # Find active or frozen membership
            for ms in self.data_manager.membership_history:
                if ms['member_id'] == member_id:
                    if ms['status'] == 'Active':
                        status = "Active"
                    elif ms['status'] == 'Frozen':
                        status = "Frozen"
                    else:
                        continue

                    plan = self.data_manager.get_plan(ms['plan_id'])
                    if plan:
                        plan_name = plan['name']
                        
                    if ms.get('assigned_trainer_id'):
                        trainer = self.data_manager.get_trainer(ms['assigned_trainer_id'])
                        if trainer:
                            trainer_name = f"{trainer['first_name']} {trainer['last_name']}"
                    break
            
            self.tree.insert("", "end", values=(
                member_id,
                member['first_name'],
                member['last_name'],
                member['contact'],
                plan_name,
                trainer_name,
                status
            ))

    def open_add_member_popup(self):
        AddMemberPopup(self)

    def open_edit_member_popup(self):
        selected = self.tree.selection()
        if not selected:
            return
        member_id = self.tree.item(selected[0])['values'][0]
        member = self.data_manager.get_member(member_id)
        if member:
             EditMemberPopup(self, member_id)

    def delete_member(self):
        selected = self.tree.selection()
        if not selected:
            return
        member_id = self.tree.item(selected[0])['values'][0]
        member = self.data_manager.get_member(member_id)
        if member:
            confirm = tk.messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {member['first_name']} {member['last_name']}? This cannot be undone.")
            if confirm:
                del self.data_manager.members_db[member_id]
                self.data_manager.save_data("members.json")
                self.populate_table()

    def open_member_profile(self):
        selected = self.tree.selection()
        if not selected:
            return
        member_id = self.tree.item(selected[0])['values'][0]
        MemberProfilePopup(self, member_id)

class AddMemberPopup(ctk.CTkToplevel):
    def __init__(self, parent_ui, initial_data=None):
        super().__init__()
        self.parent_ui = parent_ui
        self.data_manager = parent_ui.data_manager
        self.initial_data = initial_data or {}
        
        self.title("Add New Member")
        self.geometry("500x600")
        
        self.setup_ui()
        self.grab_set() # Modal

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        
        # --- Member Details ---
        ctk.CTkLabel(self, text="Member Details", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(20, 10))

        ctk.CTkLabel(self, text="First Name:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.fname_entry = ctk.CTkEntry(self)
        self.fname_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        if 'first_name' in self.initial_data:
            self.fname_entry.insert(0, self.initial_data['first_name'])
        
        ctk.CTkLabel(self, text="Last Name:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.lname_entry = ctk.CTkEntry(self)
        self.lname_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        if 'last_name' in self.initial_data:
            self.lname_entry.insert(0, self.initial_data['last_name'])
        
        ctk.CTkLabel(self, text="Contact:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.contact_entry = ctk.CTkEntry(self)
        self.contact_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        if 'contact' in self.initial_data:
            self.contact_entry.insert(0, self.initial_data['contact'])

        # --- Membership Details ---
        ctk.CTkLabel(self, text="Membership Details", font=ctk.CTkFont(size=16, weight="bold")).grid(row=4, column=0, columnspan=2, pady=(20, 10))

        # Plan Selection
        ctk.CTkLabel(self, text="Select Plan:").grid(row=5, column=0, padx=20, pady=10, sticky="w")
        self.plan_vars = [f"{pid}: {p['name']} (${p['base_price']})" for pid, p in self.data_manager.plans_db.items()]
        self.plan_combo = ctk.CTkComboBox(self, values=self.plan_vars)
        self.plan_combo.grid(row=5, column=1, padx=20, pady=10, sticky="ew")
        
        # Trainer Selection
        ctk.CTkLabel(self, text="Select Trainer (Optional):").grid(row=6, column=0, padx=20, pady=10, sticky="w")
        self.trainer_vars = ["None"] + [f"{tid}: {t['first_name']} {t['last_name']} (+${t['fee']})" for tid, t in self.data_manager.trainers_db.items()]
        self.trainer_combo = ctk.CTkComboBox(self, values=self.trainer_vars)
        self.trainer_combo.grid(row=6, column=1, padx=20, pady=10, sticky="ew")
        
        self.save_btn = ctk.CTkButton(self, text="Save Member & Membership", command=self.save_all)
        self.save_btn.grid(row=7, column=0, columnspan=2, padx=20, pady=30)

    def save_all(self):
        # Import validation function
        from ..whatsapp_helper import validate_phone_number
        
        # 1. Validate Member Data
        fname = self.fname_entry.get().strip()
        lname = self.lname_entry.get().strip()
        contact = self.contact_entry.get().strip()
        
        if not fname or not lname:
            tk.messagebox.showerror("Validation Error", "First name and last name are required")
            return
        
        # Validate contact number
        if contact:
            valid, message = validate_phone_number(contact)
            if not valid:
                tk.messagebox.showerror("Invalid Phone Number", f"{message}\\n\\nValid formats:\\n+923001234567\\n03001234567\\n923001234567")
                self.contact_entry.configure(border_color="red")
                return
            else:
                self.contact_entry.configure(border_color="")  # Reset border
            
        # 2. Validate Membership Data
        plan_str = self.plan_combo.get()
        trainer_str = self.trainer_combo.get()
        
        if not plan_str:
            tk.messagebox.showerror("Validation Error", "Please select a membership plan")
            return

        # 3. Create Member
        member_id = generate_unique_id("M")
        new_member = {
            "first_name": fname,
            "last_name": lname,
            "contact": contact,
            "join_date": get_current_date_iso()
        }
        self.data_manager.add_member(member_id, new_member)

        # 4. Create Membership
        plan_id = plan_str.split(":")[0]
        trainer_id = trainer_str.split(":")[0] if trainer_str != "None" else None
        
        plan = self.data_manager.get_plan(plan_id)
        trainer = self.data_manager.get_trainer(trainer_id) if trainer_id else None
        
        # Calculate Dates
        start_date = get_current_date_iso()
        end_date = calculate_end_date(start_date, plan['duration_months'])
        
        ms_id = generate_unique_id("MS")
        membership = {
            "membership_id": ms_id,
            "member_id": member_id,
            "plan_id": plan_id,
            "assigned_trainer_id": trainer_id,
            "start_date": start_date,
            "end_date": end_date,
            "status": "Active"
        }
        self.data_manager.membership_history.append(membership)
        self.data_manager.save_data("membership_history.json")
        
        # 5. Generate Payment
        amount = plan['base_price']
        if trainer:
            amount += trainer['fee']
            
        payment_id = generate_unique_id("PAY")
        payment = {
            "payment_id": payment_id,
            "member_id": member_id,
            "membership_id": ms_id,
            "amount_due": amount,
            "amount_paid": 0.0,
            "due_date": start_date,
            "payment_date": None,
            "status": "Unpaid"
        }
        self.data_manager.payments_log.append(payment)
        self.data_manager.save_data("payments_log.json")
        
        # 6. Finish
        self.parent_ui.populate_table()
        self.destroy()

class MemberProfilePopup(ctk.CTkToplevel):
    def __init__(self, parent_ui, member_id):
        super().__init__()
        self.data_manager = parent_ui.data_manager
        self.member_id = member_id
        self.member = self.data_manager.get_member(member_id)
        
        self.title(f"Profile: {self.member['first_name']} {self.member['last_name']}")
        self.geometry("700x600")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, height=100, fg_color=SIDEBAR_COLOR)
        header.pack(fill="x")
        
        name_lbl = ctk.CTkLabel(header, text=f"{self.member['first_name']} {self.member['last_name']}", font=ctk.CTkFont(size=24, weight="bold"))
        name_lbl.pack(pady=(20, 5))
        
        # Contact info with WhatsApp button
        contact_frame = ctk.CTkFrame(header, fg_color="transparent")
        contact_frame.pack(pady=(0, 20))
        
        contact_lbl = ctk.CTkLabel(
            contact_frame, 
            text=f"ID: {self.member_id} | Contact: {self.member['contact']}", 
            text_color=TEXT_SECONDARY_COLOR
        )
        contact_lbl.pack(side="left", padx=5)
        
        # WhatsApp button if contact exists
        if self.member.get('contact'):
            whatsapp_btn = ctk.CTkButton(
                contact_frame,
                text="💬 WhatsApp",
                command=self.open_whatsapp,
                fg_color="#25D366",
                hover_color="#128C7E",
                width=100,
                height=25,
                font=ctk.CTkFont(size=11)
            )
            whatsapp_btn.pack(side="left", padx=5)
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tabview.add("Membership History")
        self.tabview.add("Payments")
        self.tabview.add("Attendance")
        
        self.build_membership_tab()
        self.build_payments_tab()
        self.build_attendance_tab()
    
    def open_whatsapp(self):
        """Opens WhatsApp chat with member."""
        from ..whatsapp_helper import open_whatsapp_chat
        
        contact = self.member.get('contact', '')
        if contact:
            success, message = open_whatsapp_chat(contact)
            if not success:
                tk.messagebox.showerror("WhatsApp Error", message)
    
    def build_membership_tab(self):
        from ..freeze_manager import FreezeManager
        from .freeze_popup import FreezeMembershipPopup
        
        frame = self.tabview.tab("Membership History")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        
        # Get membership history
        history = [m for m in self.data_manager.membership_history if m['member_id'] == self.member_id]
        
        # Controls frame
        controls_frame = ctk.CTkFrame(frame, fg_color="transparent")
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
    def build_membership_tab(self):
        frame = self.tabview.tab("Membership History")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0) # Logs
        
        # --- Membership Table ---
        columns = ("id", "plan", "trainer", "start", "end", "status", "freeze_days")
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        
        tree.heading("id", text="ID")
        tree.heading("plan", text="Plan")
        tree.heading("trainer", text="Trainer")
        tree.heading("start", text="Start Date")
        tree.heading("end", text="End Date")
        tree.heading("status", text="Status")
        tree.heading("freeze_days", text="Freeze Days")
        
        tree.column("id", width=80)
        tree.column("plan", width=120)
        tree.column("trainer", width=120)
        tree.column("start", width=90)
        tree.column("end", width=90)
        tree.column("status", width=80)
        tree.column("freeze_days", width=80)
        
        scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)
        
        # Populate Table
        history = [m for m in self.data_manager.membership_history if m['member_id'] == self.member_id]
        history.sort(key=lambda x: x['start_date'], reverse=True)
        
        for h in history:
            plan = self.data_manager.get_plan(h['plan_id'])
            plan_name = plan['name'] if plan else "Unknown"
            
            trainer_name = "None"
            if h.get('assigned_trainer_id'):
                trainer = self.data_manager.get_trainer(h['assigned_trainer_id'])
                if trainer:
                    trainer_name = f"{trainer['first_name']} {trainer['last_name']}"
            
            tree.insert("", "end", values=(
                h['membership_id'],
                plan_name,
                trainer_name,
                h['start_date'],
                h['end_date'],
                h['status'],
                h.get('total_freeze_days', 0)
            ))
            
        # --- Freeze Logs Section ---
        logs_frame = ctk.CTkFrame(frame, fg_color=SIDEBAR_COLOR)
        logs_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(logs_frame, text="Freeze Logs (Select membership above to view)", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.logs_text = ctk.CTkTextbox(logs_frame, height=100)
        self.logs_text.pack(fill="x", padx=10, pady=(0, 10))
        self.logs_text.configure(state="disabled")
        
        # Bind selection
        def on_select(event):
            selected = tree.selection()
            if not selected:
                return
            
            item = tree.item(selected[0])
            ms_id = item['values'][0]
            
            # Find membership
            ms = next((m for m in history if m['membership_id'] == ms_id), None)
            
            self.logs_text.configure(state="normal")
            self.logs_text.delete("1.0", "end")
            
            if ms and ms.get('freeze_history'):
                for freeze in ms['freeze_history']:
                    self.logs_text.insert("end", f"• {freeze['freeze_start']} to {freeze['freeze_end']} ({freeze['freeze_days']} days)\n")
                    self.logs_text.insert("end", f"  Reason: {freeze['reason']}\n\n")
            else:
                self.logs_text.insert("end", "No freeze history for this membership.")
                
            self.logs_text.configure(state="disabled")
            
        tree.bind("<<TreeviewSelect>>", on_select)

    def build_payments_tab(self):
        frame = self.tabview.tab("Payments")
        
        # Create Treeview
        columns = ("id", "amount", "status", "due_date", "paid_date")
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        
        tree.heading("id", text="Payment ID")
        tree.heading("amount", text="Amount")
        tree.heading("status", text="Status")
        tree.heading("due_date", text="Due Date")
        tree.heading("paid_date", text="Paid Date")
        
        tree.column("id", width=100)
        tree.column("amount", width=80)
        tree.column("status", width=80)
        tree.column("due_date", width=100)
        tree.column("paid_date", width=100)
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Populate
        payments = [p for p in self.data_manager.payments_log if p['member_id'] == self.member_id]
        payments.sort(key=lambda x: x['due_date'], reverse=True)
        
        for p in payments:
            tree.insert("", "end", values=(
                p['payment_id'],
                f"${p['amount_due']}",
                p['status'],
                p['due_date'],
                p.get('payment_date') or "-"
            ))

    def build_attendance_tab(self):
        frame = self.tabview.tab("Attendance")
        
        # Create Treeview
        columns = ("date", "check_in", "check_out", "duration")
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        
        tree.heading("date", text="Date")
        tree.heading("check_in", text="Check In")
        tree.heading("check_out", text="Check Out")
        tree.heading("duration", text="Duration")
        
        tree.column("date", width=100)
        tree.column("check_in", width=100)
        tree.column("check_out", width=100)
        tree.column("duration", width=100)
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Populate
        logs = [a for a in self.data_manager.attendance_log if a['member_id'] == self.member_id]
        logs.sort(key=lambda x: x['check_in_time'], reverse=True)
        
        for l in logs:
            # Parse times
            try:
                check_in_dt = l['check_in_time']
                date_str = check_in_dt.split(" ")[0] if " " in check_in_dt else check_in_dt.split("T")[0]
                
                if "T" in check_in_dt:
                    in_time = check_in_dt.split("T")[1]
                else:
                    in_time = check_in_dt.split(" ")[1]
            except:
                date_str = l['check_in_time']
                in_time = "-"
            
            out_time = "-"
            duration = "-"
            
            if l.get('check_out_time'):
                try:
                    if "T" in l['check_out_time']:
                        out_time = l['check_out_time'].split("T")[1]
                    else:
                        out_time = l['check_out_time'].split(" ")[1]
                except:
                    out_time = l['check_out_time']
                
                if l.get('duration_minutes'):
                    duration = f"{l['duration_minutes']} min"
            
            tree.insert("", "end", values=(
                date_str,
                in_time,
                out_time,
                duration
            ))

class EditMemberPopup(ctk.CTkToplevel):
    def __init__(self, parent_ui, member_id):
        super().__init__()
        self.parent_ui = parent_ui
        self.data_manager = parent_ui.data_manager
        self.member_id = member_id
        self.member = self.data_manager.get_member(member_id)
        
        # Find latest membership for editing (regardless of status)
        self.latest_membership = None
        member_memberships = [m for m in self.data_manager.membership_history if m['member_id'] == member_id]
        if member_memberships:
            # Sort by start date descending
            member_memberships.sort(key=lambda x: x['start_date'], reverse=True)
            self.latest_membership = member_memberships[0]
        
        self.title("Edit Member Details")
        self.geometry("500x700")
        
        self.setup_ui()
        self.grab_set()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        
        # --- Personal Info ---
        ctk.CTkLabel(self, text="Personal Info", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(10, 5))

        ctk.CTkLabel(self, text="First Name:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.fname_entry = ctk.CTkEntry(self)
        self.fname_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        self.fname_entry.insert(0, self.member['first_name'])
        
        ctk.CTkLabel(self, text="Last Name:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.lname_entry = ctk.CTkEntry(self)
        self.lname_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        self.lname_entry.insert(0, self.member['last_name'])
        
        ctk.CTkLabel(self, text="Contact:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.contact_entry = ctk.CTkEntry(self)
        self.contact_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        self.contact_entry.insert(0, self.member['contact'])

        # --- Membership Info ---
        ctk.CTkLabel(self, text="Membership Info", font=ctk.CTkFont(size=14, weight="bold")).grid(row=4, column=0, columnspan=2, pady=(20, 5))
        
        ctk.CTkLabel(self, text="Current Plan:").grid(row=5, column=0, padx=20, pady=10, sticky="w")
        current_plan_id = self.latest_membership['plan_id'] if self.latest_membership else "None"
        self.plan_vars = [f"{pid}: {p['name']}" for pid, p in self.data_manager.plans_db.items()]
        self.plan_combo = ctk.CTkComboBox(self, values=self.plan_vars)
        self.plan_combo.grid(row=5, column=1, padx=20, pady=10, sticky="ew")
        if self.latest_membership:
            for p in self.plan_vars:
                if p.startswith(current_plan_id):
                    self.plan_combo.set(p)
                    break
        else:
            self.plan_combo.set("No Membership Found")
            self.plan_combo.configure(state="disabled")

        ctk.CTkLabel(self, text="Trainer:").grid(row=6, column=0, padx=20, pady=10, sticky="w")
        self.trainer_vars = ["None"] + [f"{tid}: {t['first_name']} {t['last_name']}" for tid, t in self.data_manager.trainers_db.items()]
        self.trainer_combo = ctk.CTkComboBox(self, values=self.trainer_vars)
        self.trainer_combo.grid(row=6, column=1, padx=20, pady=10, sticky="ew")
        if self.latest_membership:
             tid = self.latest_membership.get('assigned_trainer_id')
             if tid:
                 for t in self.trainer_vars:
                     if t.startswith(tid):
                         self.trainer_combo.set(t)
                         break
             else:
                 self.trainer_combo.set("None")
        else:
            self.trainer_combo.configure(state="disabled")

        ctk.CTkLabel(self, text="Status:").grid(row=7, column=0, padx=20, pady=10, sticky="w")
        self.status_combo = ctk.CTkComboBox(self, values=["Active", "Frozen", "Expired", "Cancelled"], command=self.on_status_change)
        self.status_combo.grid(row=7, column=1, padx=20, pady=10, sticky="ew")
        
        if self.latest_membership:
            self.status_combo.set(self.latest_membership['status'])
        else:
            self.status_combo.set("Inactive")
            self.status_combo.configure(state="disabled")

        # Freeze Duration (Hidden by default unless Frozen is selected)
        ctk.CTkLabel(self, text="Freeze Duration:").grid(row=8, column=0, padx=20, pady=10, sticky="w")
        self.freeze_duration_combo = ctk.CTkComboBox(self, values=["1 Month", "2 Months", "3 Months"])
        self.freeze_duration_combo.grid(row=8, column=1, padx=20, pady=10, sticky="ew")
        
        # Notes
        ctk.CTkLabel(self, text="Notes / Reason:").grid(row=9, column=0, padx=20, pady=10, sticky="nw")
        self.notes_entry = ctk.CTkTextbox(self, height=60)
        self.notes_entry.grid(row=9, column=1, padx=20, pady=10, sticky="ew")

        # Actions
        self.save_btn = ctk.CTkButton(self, text="Save Changes", command=self.save_changes)
        self.save_btn.grid(row=10, column=0, columnspan=2, padx=20, pady=20)
        
        self.on_status_change(self.status_combo.get())

    def on_status_change(self, choice):
        if choice == "Frozen":
            self.freeze_duration_combo.configure(state="normal")
            
            # Calculate remaining months
            if self.latest_membership and self.latest_membership.get('end_date'):
                try:
                    end_date = datetime.date.fromisoformat(self.latest_membership['end_date'])
                    today = datetime.date.today()
                    remaining_days = (end_date - today).days
                    
                    if remaining_days < 30:
                        self.freeze_duration_combo.configure(values=["Not enough time (< 30 days)"])
                        self.freeze_duration_combo.set("Not enough time (< 30 days)")
                        self.freeze_duration_combo.configure(state="disabled")
                    else:
                        max_months = remaining_days // 30
                        # Cap at reasonable limit (e.g., 6 months or 12 months) if needed, but user asked for remaining
                        options = [f"{i} Month{'s' if i > 1 else ''}" for i in range(1, max_months + 1)]
                        self.freeze_duration_combo.configure(values=options)
                        self.freeze_duration_combo.set(options[0])
                        self.freeze_duration_combo.configure(state="normal")
                except ValueError:
                    self.freeze_duration_combo.set("Error calculating dates")
                    self.freeze_duration_combo.configure(state="disabled")
            else:
                 self.freeze_duration_combo.set("No end date found")
                 self.freeze_duration_combo.configure(state="disabled")
                 
        else:
            self.freeze_duration_combo.configure(state="disabled")

    def save_changes(self):
        # Update Member Details
        self.member['first_name'] = self.fname_entry.get()
        self.member['last_name'] = self.lname_entry.get()
        self.member['contact'] = self.contact_entry.get()
        
        # Update Membership Details
        if self.latest_membership:
            # Track original plan and trainer for change detection
            original_plan_id = self.latest_membership['plan_id']
            original_trainer_id = self.latest_membership.get('assigned_trainer_id')
            
            # Plan
            plan_str = self.plan_combo.get()
            if plan_str and plan_str != "No Membership Found":
                new_plan_id = plan_str.split(":")[0]
                self.latest_membership['plan_id'] = new_plan_id
            else:
                new_plan_id = original_plan_id
            
            # Trainer
            trainer_str = self.trainer_combo.get()
            if trainer_str == "None":
                new_trainer_id = None
                self.latest_membership['assigned_trainer_id'] = None
            elif trainer_str:
                new_trainer_id = trainer_str.split(":")[0]
                self.latest_membership['assigned_trainer_id'] = new_trainer_id
            else:
                new_trainer_id = original_trainer_id
            
            # Detect plan or trainer change and create new payment record
            if (new_plan_id != original_plan_id or new_trainer_id != original_trainer_id):
                # Get plan and trainer details
                plan = self.data_manager.get_plan(new_plan_id)
                trainer = self.data_manager.get_trainer(new_trainer_id) if new_trainer_id else None
                
                # Calculate new amount
                amount = plan['base_price'] if plan else 0.0
                if trainer:
                    amount += trainer['fee']
                
                # Create new payment record
                payment_id = generate_unique_id("PAY")
                new_payment = {
                    "payment_id": payment_id,
                    "member_id": self.member_id,
                    "membership_id": self.latest_membership['membership_id'],
                    "amount_due": amount,
                    "amount_paid": 0.0,
                    "due_date": get_current_date_iso(),
                    "payment_date": None,
                    "status": "Unpaid"
                }
                
                self.data_manager.payments_log.append(new_payment)
                self.data_manager.save_data("payments_log.json")
                
                tk.messagebox.showinfo("Payment Created", 
                    f"Created new unpaid payment record (${amount}) for plan/trainer change.")
                
            # Status Change Logic
            new_status = self.status_combo.get()
            old_status = self.latest_membership['status']
            
            if new_status != old_status:
                self.latest_membership['status'] = new_status
                
                # Log the change
                if 'status_history' not in self.latest_membership:
                    self.latest_membership['status_history'] = []
                
                note = self.notes_entry.get("1.0", "end-1c").strip()
                self.latest_membership['status_history'].append({
                    "date": get_current_date_iso(),
                    "old_status": old_status,
                    "new_status": new_status,
                    "note": note
                })
                
                # Handle Freeze Logic
                if new_status == "Frozen":
                    duration_str = self.freeze_duration_combo.get()
                    if not duration_str or "Month" not in duration_str:
                         tk.messagebox.showerror("Error", "Cannot freeze: Invalid duration or not enough time remaining.")
                         return

                    months = int(duration_str.split(" ")[0])
                    
                    freeze_start = get_current_date_iso()
                    freeze_end = calculate_end_date(freeze_start, months)
                    
                    if 'freeze_history' not in self.latest_membership:
                        self.latest_membership['freeze_history'] = []
                        
                    self.latest_membership['freeze_history'].append({
                        "freeze_id": generate_unique_id("F"),
                        "freeze_start": freeze_start,
                        "freeze_end": freeze_end,
                        "reason": note or "Manual Status Change",
                        "approved_by": "admin",
                        "freeze_days": months * 30
                    })
                    
                    # Extend membership end date
                    if 'total_freeze_days' not in self.latest_membership:
                        self.latest_membership['total_freeze_days'] = 0
                    self.latest_membership['total_freeze_days'] += (months * 30)
                    
                    current_end = self.latest_membership['end_date']
                    new_end = calculate_end_date(current_end, months)
                    self.latest_membership['end_date'] = new_end
                
                # Handle Expired Logic - Delete unpaid payments
                elif new_status == "Expired":
                    # Find all unpaid payments for this membership
                    membership_id = self.latest_membership['membership_id']
                    payments_to_delete = []
                    
                    for payment in self.data_manager.payments_log:
                        if payment.get('membership_id') == membership_id and payment['status'] == 'Unpaid':
                            payments_to_delete.append(payment)
                    
                    # Delete the payments
                    for payment in payments_to_delete:
                        self.data_manager.payments_log.remove(payment)
                    
                    # Save the updated payments log
                    if payments_to_delete:
                        self.data_manager.save_data("payments_log.json")
                        tk.messagebox.showinfo("Payments Deleted", 
                            f"Deleted {len(payments_to_delete)} unpaid payment(s) for this expired membership.")
                
                # Handle Reactivation - Create new unpaid payment when expired member is reactivated
                elif old_status == "Expired" and new_status == "Active":
                    membership_id = self.latest_membership['membership_id']
                    plan_id = self.latest_membership['plan_id']
                    trainer_id = self.latest_membership.get('assigned_trainer_id')
                    
                    # Get plan and trainer details
                    plan = self.data_manager.get_plan(plan_id)
                    trainer = self.data_manager.get_trainer(trainer_id) if trainer_id else None
                    
                    # Calculate amount
                    amount = plan['base_price'] if plan else 0.0
                    if trainer:
                        amount += trainer['fee']
                    
                    # Create new payment record
                    payment_id = generate_unique_id("PAY")
                    new_payment = {
                        "payment_id": payment_id,
                        "member_id": self.member_id,
                        "membership_id": membership_id,
                        "amount_due": amount,
                        "amount_paid": 0.0,
                        "due_date": get_current_date_iso(),
                        "payment_date": None,
                        "status": "Unpaid"
                    }
                    
                    self.data_manager.payments_log.append(new_payment)
                    self.data_manager.save_data("payments_log.json")
                    
                    tk.messagebox.showinfo("Payment Created", 
                        f"Created new unpaid payment record (${amount}) for reactivated membership.")
            
            self.data_manager.save_data("membership_history.json")

        self.data_manager.save_data("members.json")
        self.parent_ui.populate_table()
        self.destroy()
