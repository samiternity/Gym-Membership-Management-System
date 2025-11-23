Here is a well-documented application design model for your Gym Management System using `CustomTkinter`.

This model breaks down each module, its user interface (UI) components, its key functions (logic), and how it interacts with your data structures.

---

### 1. Overall Application Design (`App` Class)

This is the main application class that inherits from `customtkinter.CTk`. It's the "shell" that holds everything.

* **UI Description:**
    * The main application window (`tk.Tk()` root).
    * It's divided into two main `CTkFrame` widgets:
        1.  **`sidebar_frame` (Left):** A narrow, static frame with `CTkButton` widgets for each module (Dashboard, Members, etc.).
        2.  **`content_frame` (Right):** A large, dynamic frame. Its contents are **destroyed and rebuilt** every time a new module is selected.
* **Key Functions (Logic):**
    * **`__init__(self)`:** Initializes the main window, creates the sidebar and content frames, and calls the `DataManager` to load all data into memory.
    * **`data_manager.load_all_data()`:** Reads all JSON files (`members.json`, `payments_log.json`, etc.) into instance variables (e.g., `self.members_db`, `self.payments_log`).
    * **`data_manager.save_all_data()`:** Writes the *current state* of all in-memory data back to the JSON files. This is a critical function.
    * **`on_close_app(self)`:** A function tied to the window's "X" button. It calls `save_all_data()` *before* destroying the window to prevent data loss.
    * **Navigation Functions (e.g., `show_dashboard_module(self)`)**:
        1.  Destroys all current widgets in `content_frame`.
        2.  Calls the specific module's build function (e.g., `build_dashboard_ui(self, self.content_frame)`).
* **Data Interaction:**
    * **Holds all data** as instance variables (e.g., `self.members_db`, `self.membership_history`).
    * Passes itself (using `self`) to sub-modules so they can access and modify this central data.

---

### 2. Module: Dashboard

* **UI Description:**
    * A main `CTkFrame` using a `.grid()` layout.
    * **Top Row:** A `CTkFrame` containing three "Stat Card" `CTkFrame` widgets. Each card has:
        * `CTkLabel` (e.g., "Total Members").
        * `CTkLabel` (e.g., "1245") with a larger font.
    * **Bottom Row:** Two `CTkFrame` widgets, each one containing a `matplotlib` canvas for a chart.
* **Key Functions (Logic):**
    * **`build_dashboard_ui(self, parent_frame)`:** Creates all the UI widgets and places them in the `parent_frame`.
    * **`load_dashboard_stats(self)`:** This function runs to get the numbers for the stat cards.
        * `total_members = len(self.members_db)`
        * `pending_payments = len([p for p in self.payments_log if p['status'] == 'Unpaid'])`
        * `active_check_ins = len([a for a in self.attendance_log if a['check_out_time'] is None])`
        * It then updates the text of the `CTkLabel` widgets.
    * **`plot_financial_graph(self, chart_frame)`:**
        * Calls your `get_monthly_income_data()` helper function.
        * Uses `matplotlib` to create a bar chart of the returned data.
        * Embeds the chart in the `chart_frame`.
    * **`plot_peak_hours_graph(self, chart_frame)`:**
        * Uses `collections.Counter` to process `self.attendance_log`.
        * Extracts the `check_in_time` hour for each log.
        * Creates and embeds a `matplotlib` bar chart.
* **Data Interaction:**
    * **Read-Only:** Reads from `self.members_db`, `self.payments_log`, and `self.attendance_log`.
    * **No data is written** from this module.

---

### 3. Module: Member Management

* **UI Description:**
    * **Top "Control" Frame:** A `CTkFrame` with:
        * `CTkButton` (e.g., "+ Add New Member").
        * `CTkButton` (e.g., "View/Edit Selected").
        * `CTkButton` (e.g., "Manage Memberships").
        * `CTkEntry` (for search).
    * **Main "Table" Frame:** A `ttk.Treeview` widget (which you will style to match) inside a `CTkFrame` with a `CTkScrollbar`.
* **Key Functions (Logic):**
    * **`build_member_ui(self, parent_frame)`:** Creates the UI elements.
    * **`populate_member_table(self, filter_query=None)`:**
        * Clears the `Treeview`.
        * Loops through `self.members_db`.
        * For each member, it finds their *current active membership* (if any) in `self.membership_history` to get their status.
        * If `filter_query` is present, it only shows matching names.
        * Inserts the row into the `Treeview`.
    * **`open_add_member_popup(self)`:**
        * Opens a new `customtkinter.CTkToplevel` window.
        * This window is a form with `CTkEntry` widgets for `first_name`, `last_name`, `contact`.
        * On "Save," it creates the new member in `self.members_db`, then *automatically* opens the "Add New Membership" pop-up to create their first contract.
    * **`open_member_profile_popup(self)`:**
        * Gets the `member_id` from the selected `Treeview` row.
        * Calls a helper function `get_full_member_profile(member_id)` (as we designed) to gather all their data.
        * Displays this data in a new `CTkToplevel` window, probably using a `CTkTabview` with tabs for "Profile", "Payment History", "Attendance History," and "Membership History".
* **Data Interaction:**
    * **Reads:** `self.members_db`, `self.membership_history`, `self.payments_log`, `self.attendance_log`.
    * **Writes:** Creates new entries in `self.members_db`, `self.membership_history`, and `self.payments_log` (via the "Add Member" and "Add Membership" pop-ups).

---

### 4. Module: Trainer Management

* **UI Description:**
    * Virtually identical to the Member Management module: A top "Control" Frame and a main `Treeview` frame.
    * `Treeview` Columns: Trainer ID, Name, Specialization, Contact, Fee, Status.
* **Key Functions (Logic):**
    * **`build_trainer_ui(self, parent_frame)`:** Creates the UI.
    * **`populate_trainer_table(self)`:** Loops through `self.trainers_db` and fills the `Treeview`.
    * **`open_add_edit_trainer_popup(self, trainer_id=None)`:**
        * Opens a `CTkToplevel` form.
        * If `trainer_id` is `None`, it's an "Add" form.
        * If `trainer_id` is provided, it's an "Edit" form, and all `CTkEntry` widgets are pre-filled with data from `self.trainers_db[trainer_id]`.
    * **`on_save_trainer(self, form_data, trainer_id=None)`:**
        * If `trainer_id` is `None`, generates a new ID and adds a new dictionary to `self.trainers_db`.
        * If `trainer_id` exists, it updates the existing dictionary `self.trainers_db[trainer_id]` with the new `form_data`.
        * Calls `save_all_data()` and refreshes the table.
* **Data Interaction:**
    * **Read/Write:** Full CRUD operations on `self.trainers_db`.

---

### 5. Module: Payment Management

* **UI Description:**
    * **Top "Control" Frame:**
        * `CTkCheckBox` ("Show Unpaid Members Only"). This is a key feature.
        * `CTkButton` ("Mark Selected as Paid").
    * **Main "Table" Frame:** A `ttk.Treeview` with a `CTkScrollbar`.
    * **`Treeview` Columns:** Member Name, Amount Due, Due Date, Status.
* **Key Functions (Logic):**
    * **`build_payment_ui(self, parent_frame)`:** Creates the UI.
    * **`populate_payments_table(self)`:**
        * Checks the state of the "Unpaid Only" `CTkCheckBox`.
        * Loops through `self.payments_log`.
        * If the box is checked, it only processes records where `status == 'Unpaid'`.
        * Gets the member's name from `self.members_db` using the `member_id`.
        * Inserts the row into the `Treeview`. Use `Treeview.tag_configure()` to color-code "Unpaid" rows as red.
    * **`on_mark_as_paid(self)`:**
        * Gets the `payment_id` from the selected `Treeview` row.
        * Finds the corresponding dictionary in `self.payments_log`.
        * Sets `status = "Paid"`, `amount_paid = amount_due`, and `payment_date = datetime.now()`.
        * Calls `save_all_data()` and refreshes the table.
* **Data Interaction:**
    * **Reads:** `self.payments_log` and `self.members_db` (for names).
    * **Writes:** Modifies entries in `self.payments_log`.

---

### 6. Module: Attendance Tracking

* **UI Description:**
    * **Top "Action" Frame:**
        * `CTkLabel` ("Enter Member ID:").
        * `CTkEntry` (for the ID). This should be the main focus.
        * `CTkButton` ("Check In") and `CTkButton` ("Check Out").
    * **Bottom "Log" Frame:**
        * `CTkLabel` ("Today's Activity").
        * A `ttk.Treeview` to show a live log of today's check-ins and check-outs.
* **Key Functions (Logic):**
    * **`build_attendance_ui(self, parent_frame)`:** Creates the UI.
    * **`on_check_in(self)`:**
        1.  Gets `member_id` from the `CTkEntry`.
        2.  Verifies the member exists in `self.members_db`.
        3.  Checks if member is already checked in (finds a log entry with this `member_id` and `check_out_time is None`). If so, show an error.
        4.  Creates a new `log_entry` dictionary with a new `log_id`, the `member_id`, and `check_in_time`.
        5.  Appends this entry to `self.attendance_log`, calls `save_all_data()`, and refreshes the "Today's Activity" table.
    * **`on_check_out(self)`:**
        1.  Gets `member_id`.
        2.  Finds the active log entry for this `member_id` (where `check_out_time is None`). If not found, show an error.
        3.  Sets `check_out_time` to the current time.
        4.  Calculates the `duration_minutes` and adds it.
        5.  Calls `save_all_data()` and refreshes the table.
* **Data Interaction:**
    * **Read/Write:** Full CRUD operations on `self.attendance_log`.
    * **Reads:** `self.members_db` (to verify member exists).

---

### 7. Module: Visitors (New Module)

* **UI Description:**
    * Very similar to Trainer Management. A `Treeview` to list all visitors.
    * Controls: `+ Add Visitor`, "Edit Visitor", and a `CTkButton` ("Convert to Member").
* **Key Functions (Logic):**
    * **`build_visitor_ui(self, parent_frame)`:** Creates the UI.
    * **`populate_visitor_table(self)`:** Loops `self.visitors_log` and fills the `Treeview`.
    * **`open_add_edit_visitor_popup(self, visitor_id=None)`:** Opens a form to add/edit visitor details.
    * **`on_convert_to_member(self)`:**
        1.  Gets the selected `visitor_id` from the `Treeview`.
        2.  Gathers the visitor's data (name, contact) from `self.visitors_log`.
        3.  Calls the `open_add_member_popup()` function *and passes the data to it*, so the form is pre-filled.
        4.  Changes the `status` of the visitor in `self.visitors_log` to "Joined".
* **Data Interaction:**
    * **Read/Write:** Full CRUD on `self.visitors_log`.
    * **Writes:** Can trigger the "Add Member" workflow, which writes to `self.members_db`.