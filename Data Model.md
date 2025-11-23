This is an excellent way to think. A well-documented data structure is the foundation of a robust application.

Here is a complete documentation for your data model, including how and where each piece of data will be used by your application.

### Overview: The Data Model

Your application will operate on a set of JSON files stored in a `data/` directory.

* **On App Start:** A `DataManager` class will load the contents of *all* these JSON files into memory as Python dictionaries and lists.
* **During App Use:** Your application will read from and write to these in-memory variables. For example, adding a new member appends to the `self.payments_log` list.
* **On App Close (or Save):** The `DataManager` will write the *entire* in-memory data back to the JSON files, overwriting them with the new, updated information.

---

### 1. `members.json` (`self.members_db`)

* **Data Structure:** Dictionary of Dictionaries. (Key: `member_id`, Value: Member Info `dict`)
* **Purpose:** A "phone book" of timeless contact info for every person who has *ever* joined.

| Variable Name (Key) | Data Type | Example Value | Description & App Usage |
| :--- | :--- | :--- | :--- |
| **`"M001"`** (Primary Key) | `str` | `"M001"` | The **unique ID** for the member. This is the **Primary Key** used to link all other data structures together. |
| `first_name` | `str` | `"Jane"` | Member's first name. **Called by:** `Member Management` table, `Member Profile` screen. |
| `last_name` | `str` | `"Doe"` | Member's last name. **Called by:** `Member Management` table, `Member Profile` screen. |
| `contact` | `str` | `"(555) 111-2222"` | Member's phone or email. **Called by:** `Member Management` table, `Member Profile` screen. |
| `join_date` | `str` (ISO Date) | `"2023-01-15"` | The date this person *first* ever registered. This **never changes**. **Called by:** `Member Profile` screen. |

---

### 2. `trainers.json` (`self.trainers_db`)

* **Data Structure:** Dictionary of Dictionaries. (Key: `trainer_id`, Value: Trainer Info `dict`)
* **Purpose:** Stores all available trainers and their specific additional fee.

| Variable Name (Key) | Data Type | Example Value | Description & App Usage |
| :--- | :--- | :--- | :--- |
| **`"T001"`** (Primary Key) | `str` | `"T001"` | The **unique ID** for the trainer. |
| `first_name` | `str` | `"Alex"` | Trainer's first name. **Called by:** `Trainer Management` table. |
| `last_name` | `str` | `"Johnson"` | Trainer's last name. **Called by:** `Trainer Management` table. |
| `specialization` | `str` | `"Yoga, Pilates"` | Trainer's specialty. **Called by:** `Trainer Management` table. |
| `contact` | `str` | `"(555) 234-5678"` | Trainer's contact info. **Called by:** `Trainer Management` table. |
| `status` | `str` | `"Active"` | ("Active", "Inactive"). **Called by:** "Add Membership" pop-up to filter the list of assignable trainers. |
| **`fee`** | `float` | `150.00` | **Crucial Variable.** The extra cost to add this trainer. **Called by:** The `calculate_total_fee()` function when a new payment record is generated. |

---

### 3. `plans.json` (`self.plans_db`)

* **Data Structure:** Dictionary of Dictionaries. (Key: `plan_id`, Value: Plan Info `dict`)
* **Purpose:** A lookup table for all available membership plans.

| Variable Name (Key) | Data Type | Example Value | Description & App Usage |
| :--- | :--- | :--- | :--- |
| **`"P01"`** (Primary Key) | `str` | `"P01"` | The **unique ID** for the plan. |
| `name` | `str` | `"Annual Gold"` | Public-facing plan name. **Called by:** `Member Profile` screen (to show the plan name, not just the ID). |
| **`base_price`** | `float` | `500.00` | **Crucial Variable.** The plan's cost *before* trainer fees. **Called by:** The `calculate_total_fee()` function. |
| `duration_days` | `int` | `365` | The plan's length. **Called by:** "Add Membership" pop-up to automatically calculate the `end_date` from the `start_date`. |

---

### 4. `membership_history.json` (`self.membership_history`)

* **Data Structure:** List of Dictionaries.
* **Purpose:** The *most important* data structure. It's the "glue" that tracks every single membership contract, including for re-joined members.

| Variable Name (Key) | Data Type | Example Value | Description & App Usage |
| :--- | :--- | :--- | :--- |
| **`membership_id`** | `str` | `"MS1001"` | The **unique ID** for this specific *contract*. **Primary Key.** |
| **`member_id`** | `str` | `"M001"` | **Foreign Key.** Links to `members_db`. **Called by:** `get_full_member_profile()` to find all contracts for a member. |
| **`plan_id`** | `str` | `"P01"` | **Foreign Key.** Links to `plans_db`. |
| **`assigned_trainer_id`** | `str` or `None` | `"T001"` | **Foreign Key.** Links to `trainers_db`. `None` if no trainer was hired. |
| `start_date` | `str` (ISO Date) | `"2023-01-15"` | The start of *this* specific contract. |
| `end_date` | `str` (ISO Date) | `"2024-01-15"` | The end of *this* specific contract. |
| `status` | `str` | `"Active"` | ("Active", "Frozen", "Expired"). **Called by:** `Member Management` table to show the status of a member's *current* active contract. |

---

### 5. `payments_log.json` (`self.payments_log`)

* **Data Structure:** List of Dictionaries.
* **Purpose:** The complete financial ledger. Tracks every bill generated.

| Variable Name (Key) | Data Type | Example Value | Description & App Usage |
| :--- | :--- | :--- | :--- |
| **`payment_id`** | `str` | `"PAY1001"` | The **unique ID** for this invoice. **Primary Key.** |
| **`member_id`** | `str` | `"M001"` | **Foreign Key.** Links to `members_db`. **Called by:** `Payment Management` table. |
| **`membership_id`** | `str` | `"MS1001"` | **Foreign Key.** Links this bill to a *specific contract*. |
| **`amount_due`** | `float` | `650.00` | The total calculated fee (`plan.base_price` + `trainer.fee`). **Called by:** `Payment Management` table. |
| `amount_paid` | `float` | `0.0` | The amount paid so far. **Called by:** "Mark as Paid" logic. |
| `due_date` | `str` (ISO Date) | `"2023-01-15"` | Date the payment is due. |
| `payment_date` | `str` or `None` | `None` | The date the bill was paid in full. `None` if unpaid. **Called by:** Financial Graph logic. |
| **`status`** | `str` | `"Unpaid"` | ("Unpaid", "Paid"). **Crucial Variable.** **Called by:** `Payment Management` (for filtering), `Dashboard` (for "Pending Payments" stat). |

---

### 6. `attendance_log.json` (`self.attendance_log`)

* **Data Structure:** List of Dictionaries.
* **Purpose:** A chronological log of all member check-ins and check-outs.

| Variable Name (Key) | Data Type | Example Value | Description & App Usage |
| :--- | :--- | :--- | :--- |
| **`log_id`** | `str` | `"A1001"` | The **unique ID** for this visit. **Primary Key.** |
| **`member_id`** | `str` | `"M001"` | **Foreign Key.** Links to `members_db`. |
| `check_in_time` | `str` (ISO 8601) | `"2025-11-17T10:00:00"` | Full timestamp. **Called by:** `Attendance Tracking` module. |
| `check_out_time` | `str` or `None` | `None` | `None` if member is still inside. **Called by:** `Dashboard` (to find "Members Checked-In"). |
| `duration_minutes` | `int` or `None` | `None` | Calculated on check-out. **Called by:** `Attendance Tracking` log. |

---

### 7. `visitors_log.json` (`self.visitors_log`)

* **Data Structure:** List of Dictionaries.
* **Purpose:** Tracks leads/trials for people who are not yet members.

| Variable Name (Key) | Data Type | Example Value | Description & App Usage |
| :--- | :--- | :--- | :--- |
| **`visitor_id`** | `str` | `"V1001"` | The **unique ID** for this visitor. **Primary Key.** |
| `first_name` | `str` | `"John"` | Visitor's name. |
| `last_name` | `str` | `"Smith"` | Visitor's name. |
| `contact` | `str` | `"(555) 888-9999"` | Visitor's contact info. |
| `visit_date` | `str` (ISO Date) | `"2025-11-16"` | Date of their trial. |
| `interested_in` | `str` | `"CrossFit"` | What service they're interested in. |
| `status` | `str` | `"Follow-up"` | ("Follow-up", "Joined", "Not Interested"). **Called by:** `Visitors` module to manage leads. |

This complete data model will allow you to build every one of your requested features.

Would you like to start outlining the step-by-step logic for the "Add New Member" process? It's the most complex one, as it has to interact with many of these structures.