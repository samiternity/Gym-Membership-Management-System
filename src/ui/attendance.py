import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime
from ..styles import *
from ..utils import *

class Attendance:
    def __init__(self, parent_frame, data_manager):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        
        self.setup_ui()
        self.populate_table()

    def setup_ui(self):
        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.parent_frame.grid_rowconfigure(0, weight=0)
        self.parent_frame.grid_rowconfigure(1, weight=1)

        # Action Frame
        self.action_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.action_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(self.action_frame, text="Search Member (ID or Name):", font=ctk.CTkFont(size=16)).pack(side="left", padx=(0, 10))
        
        self.id_entry = ctk.CTkEntry(self.action_frame, width=200)
        self.id_entry.pack(side="left", padx=(0, 20))
        self.id_entry.bind("<Return>", self.on_return_key) # Handle selection if list is open, else check-in
        self.id_entry.bind("<KeyRelease>", self.on_search_type)
        self.id_entry.bind("<Down>", self.on_arrow_down)
        self.id_entry.bind("<Up>", self.on_arrow_up)
        self.id_entry.bind("<Tab>", self.on_tab_key)
        
        # Search Results Listbox (Hidden by default)
        # Search Results Listbox (Hidden by default)
        self.search_list_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.search_list = tk.Listbox(
            self.search_list_frame, 
            height=5,
            font=("Segoe UI", 12),
            bg="#2B2B2B",
            fg="white",
            selectbackground=ACCENT_COLOR,
            selectforeground="white",
            borderwidth=1,
            relief="flat",
            exportselection=False  # Keep selection visible when losing focus
        )
        self.search_list.bind("<<ListboxSelect>>", self.on_search_select)
        
        self.check_in_btn = ctk.CTkButton(self.action_frame, text="Check In", command=self.check_in, fg_color=SUCCESS_COLOR)
        self.check_in_btn.pack(side="left", padx=(0, 10))
        
        self.check_out_btn = ctk.CTkButton(self.action_frame, text="Check Out Selected", command=self.check_out, fg_color=WARNING_COLOR)
        self.check_out_btn.pack(side="left", padx=(0, 10))

        self.delete_btn = ctk.CTkButton(self.action_frame, text="Delete Log", command=self.delete_log, fg_color=DANGER_COLOR)
        self.delete_btn.pack(side="left", padx=(0, 10))

        # Date Selection
        ctk.CTkLabel(self.action_frame, text="View Date:").pack(side="left", padx=(10, 5))
        self.date_var = ctk.StringVar(value=get_current_date_iso())
        self.date_combo = ctk.CTkComboBox(self.action_frame, variable=self.date_var, command=self.populate_table)
        self.date_combo.pack(side="left")
        self.update_date_options()

        # Log Frame
        self.log_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.log_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.log_label = ctk.CTkLabel(self.log_frame, text="Today's Activity", font=ctk.CTkFont(size=16, weight="bold"))
        self.log_label.pack(anchor="w", pady=(0, 10))
        
        columns = ("check_in", "check_out", "member_id", "name", "status", "duration")
        self.tree = ttk.Treeview(self.log_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("check_in", text="Check-In Time")
        self.tree.heading("check_out", text="Check-Out Time")
        self.tree.heading("member_id", text="Member ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("status", text="Status")
        self.tree.heading("duration", text="Duration (min)")
        
        self.tree.column("check_in", width=120, anchor="center")
        self.tree.column("check_out", width=120, anchor="center")
        self.tree.column("member_id", width=100, anchor="center")
        self.tree.column("name", width=200)
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("duration", width=100, anchor="center")

        scrollbar = ctk.CTkScrollbar(self.log_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def update_date_options(self):
        dates = set()
        for log in self.data_manager.attendance_log:
            date_str = log['check_in_time'].split("T")[0] if "T" in log['check_in_time'] else log['check_in_time'].split(" ")[0]
            dates.add(date_str)
        
        sorted_dates = sorted(list(dates), reverse=True)
        if not sorted_dates:
            sorted_dates = [get_current_date_iso()]
            
        self.date_combo.configure(values=sorted_dates)
        if get_current_date_iso() in sorted_dates:
            self.date_combo.set(get_current_date_iso())
        else:
            self.date_combo.set(sorted_dates[0])

    def populate_table(self, _=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        selected_date = self.date_var.get()
        self.log_label.configure(text=f"Activity for {selected_date}")
        
        # Filter logs for selected date
        todays_logs = []
        for log in self.data_manager.attendance_log:
            if log['check_in_time'].startswith(selected_date):
                todays_logs.append(log)
        
        # Sort by time (latest first)
        todays_logs.sort(key=lambda x: x['check_in_time'], reverse=True)
        
        for log in todays_logs:
            member = self.data_manager.get_member(log['member_id'])
            name = f"{member['first_name']} {member['last_name']}" if member else "Unknown"
            
            check_in_time = "-"
            try:
                if "T" in log['check_in_time']:
                    check_in_time = log['check_in_time'].split("T")[1]
                else:
                    check_in_time = log['check_in_time'].split(" ")[1]
            except IndexError:
                check_in_time = log['check_in_time']

            check_out_time = "-"
            status = "Checked In"
            duration = "-"
            
            if log.get('check_out_time'):
                status = "Checked Out"
                try:
                    if "T" in log['check_out_time']:
                        check_out_time = log['check_out_time'].split("T")[1]
                    else:
                        check_out_time = log['check_out_time'].split(" ")[1]
                except IndexError:
                    check_out_time = log['check_out_time']
                
                duration = str(log.get('duration_minutes', 0))
            
            self.tree.insert("", "end", values=(
                check_in_time,
                check_out_time,
                log['member_id'],
                name,
                status,
                duration,
                log['log_id'] # Hidden column for ID if needed, or just use index
            ))

    def on_search_type(self, event):
        # Ignore navigation keys
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return', 'Tab'):
            return
            
        query = self.id_entry.get().strip().lower()
        if not query:
            self.search_list_frame.place_forget()
            return
            
        matches = []
        for mid, m in self.data_manager.members_db.items():
            full_name = f"{m['first_name']} {m['last_name']}".lower()
            if query in full_name or query in mid.lower():
                matches.append(f"{mid}: {m['first_name']} {m['last_name']}")
        
        if matches:
            self.search_list.delete(0, "end")
            for match in matches[:5]: # Limit to 5
                self.search_list.insert("end", match)
            
            # Position listbox below entry
            # Use absolute positioning relative to the parent frame to ensure it floats on top
            x = self.action_frame.winfo_x() + self.id_entry.winfo_x() + 20
            y = self.action_frame.winfo_y() + self.id_entry.winfo_y() + self.id_entry.winfo_height() + 20
            
            self.search_list_frame.configure(width=200, height=100)
            self.search_list_frame.place(x=x, y=y)
            self.search_list.pack(fill="both", expand=True)
            self.search_list_frame.lift()
            self.parent_frame.update_idletasks() # Force update
        else:
            self.search_list_frame.place_forget()

    def on_search_select(self, event):
        selection = self.search_list.curselection()
        if selection:
            data = self.search_list.get(selection[0])
            member_id = data.split(":")[0]
            self.id_entry.delete(0, "end")
            self.id_entry.insert(0, member_id)
            self.search_list_frame.place_forget()
            self.check_in()

    def on_arrow_down(self, event):
        """Select next item in listbox."""
        if not self.search_list_frame.winfo_ismapped():
            return
            
        if self.search_list.size() > 0:
            current_selection = self.search_list.curselection()
            if current_selection:
                next_index = min(current_selection[0] + 1, self.search_list.size() - 1)
                self.search_list.selection_clear(0, "end")
                self.search_list.selection_set(next_index)
                self.search_list.activate(next_index)
                self.search_list.see(next_index)
            else:
                self.search_list.selection_set(0)
                self.search_list.activate(0)
                self.search_list.see(0)

    def on_arrow_up(self, event):
        """Select previous item in listbox."""
        if not self.search_list_frame.winfo_ismapped():
            return

        if self.search_list.size() > 0:
            current_selection = self.search_list.curselection()
            if current_selection:
                prev_index = max(current_selection[0] - 1, 0)
                self.search_list.selection_clear(0, "end")
                self.search_list.selection_set(prev_index)
                self.search_list.activate(prev_index)
                self.search_list.see(prev_index)

    def on_tab_key(self, event):
        """Select current item in listbox on Tab."""
        if self.search_list_frame.winfo_ismapped():
            # If nothing selected but list is open, select first item
            if not self.search_list.curselection() and self.search_list.size() > 0:
                self.search_list.selection_set(0)
            
            if self.search_list.curselection():
                self.on_search_select(None)
                return "break" # Prevent default tab behavior
        return None

    def on_return_key(self, event):
        """Handle Enter key: select from list if open, else check in."""
        if self.search_list_frame.winfo_ismapped() and self.search_list.curselection():
            self.on_search_select(None)
        else:
            self.check_in()

    def check_in(self):
        query = self.id_entry.get().strip()
        if not query:
            return
            
        # Try to find member by ID or Name
        member_id = None
        if query in self.data_manager.members_db:
            member_id = query
        else:
            # Search by name
            matches = []
            for mid, m in self.data_manager.members_db.items():
                full_name = f"{m['first_name']} {m['last_name']}".lower()
                if query.lower() in full_name:
                    matches.append(mid)
            
            if len(matches) == 1:
                member_id = matches[0]
            elif len(matches) > 1:
                messagebox.showwarning("Ambiguous", "Multiple members found with that name. Please use ID.")
                return
            else:
                messagebox.showerror("Error", "Member not found!")
                return

        # Check if already checked in
        for log in self.data_manager.attendance_log:
            if log['member_id'] == member_id and log.get('check_out_time') is None:
                messagebox.showwarning("Warning", "Member is already checked in!")
                return
        
        new_log = {
            "log_id": generate_unique_id("A"),
            "member_id": member_id,
            "check_in_time": get_current_datetime_iso(),
            "check_out_time": None,
            "duration_minutes": None
        }
        
        self.data_manager.attendance_log.append(new_log)
        self.data_manager.save_data("attendance_log.json")
        
        self.id_entry.delete(0, "end")
        self.search_list_frame.place_forget()
        self.update_date_options()
        self.populate_table()

    def check_out(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a checked-in member to check out.")
            return
            
        item = self.tree.item(selected[0])
        member_id = item['values'][2] # Member ID is at index 2
        
        # Find active log
        active_log = None
        for log in self.data_manager.attendance_log:
            if log['member_id'] == member_id and log.get('check_out_time') is None:
                active_log = log
                break
                
        if not active_log:
            messagebox.showerror("Error", "Member is not checked in or already checked out!")
            return
            
        check_out_time = get_current_datetime_iso()
        active_log['check_out_time'] = check_out_time
        
        # Calculate duration
        start = datetime.datetime.fromisoformat(active_log['check_in_time'])
        end = datetime.datetime.fromisoformat(check_out_time)
        duration = int((end - start).total_seconds() / 60)
        active_log['duration_minutes'] = duration
        
        self.data_manager.save_data("attendance_log.json")
        self.populate_table()

    def delete_log(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a log to delete.")
            return
            
        item = self.tree.item(selected[0])
        # We need to find the log ID. Since we didn't store it in visible columns, 
        # we have to infer it from member_id and check_in_time or store it.
        # Let's rely on finding the exact match in the current list.
        
        check_in_time_display = item['values'][0]
        member_id = item['values'][2]
        
        # This is tricky because display time might be truncated/formatted.
        # Better approach: Add log_id to treeview but hide it? 
        # Or just match carefully.
        
        log_to_delete = None
        for log in self.data_manager.attendance_log:
            if log['member_id'] == member_id:
                # Check if time matches
                t = log['check_in_time']
                if "T" in t: t = t.split("T")[1]
                else: t = t.split(" ")[1]
                
                if t == check_in_time_display:
                    log_to_delete = log
                    break
        
        if log_to_delete:
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this attendance record?")
            if confirm:
                self.data_manager.attendance_log.remove(log_to_delete)
                self.data_manager.save_data("attendance_log.json")
                self.populate_table()
                self.update_date_options()
        else:
            messagebox.showerror("Error", "Could not identify the log record to delete.")
