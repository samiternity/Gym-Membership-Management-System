
## Detailed Code Explanation

This section provides an in-depth explanation of the code in your primary files.

### 1. `src/analytics.py` (Business Logic)
This file generates insights from the raw data. It does not contain any UI code.

#### **Class: `Analytics`**
*   **`__init__(self, data_manager)`**: Initializes the analytics engine with access to the central data manager.

#### **Key Methods:**
1.  **Retention Calculations:**
    *   **`calculate_churn_rate(period_months, month_offset)`**:
        *   **Logic:** Calculates the percentage of members who left (expired and didn't renew) in a prior period.
        *   **How:** It iterates through `membership_history`. If a membership expired in the target window, it checks if that same `member_id` started a *new* membership afterwards. If no renewal is found, they churned.
        *   **Formula:** `(Lost Members / Total Expired Memberships) * 100`.
    *   **`calculate_retention_rate()`**: The inverse of churn rate (`100 - churn`). This is the number you show on the dashboard.
    *   **`get_retention_trend(months)`**: Loops backwards through the last `N` months, calling `calculate_retention_rate` for each month to build a trend line data set.

2.  **Risk Management:**
    *   **`get_at_risk_members(days_threshold)`**:
        *   **Logic:** Finds members whose `end_date` is within the next 30 days (or specified threshold).
        *   **Usage:** Populates the "Expiring Soon" count on the dashboard.

3.  **Financial Modeling:**
    *   **`predict_revenue(months_ahead)`**:
        *   **Logic:** Combines **Historical Average** (what we usually make) with **Guaranteed Revenue** (unpaid invoices for active members).
        *   **Algorithm:** `(Average Monthly Revenue * Variation) + (Guaranteed / Months)`.
        *   **Note:** Includes a `random.uniform(0.9, 1.1)` factor to simulate real-world fluctuation, making the graph look more realistic than a straight line.
    *   **`calculate_confidence_interval()`**: Returns a score (Low/Medium/High) based on how much data exists. If only 5 invoices exist, confidence is Low.

---

### 2. `src/ui/dashboard.py` (Visualization)
This file handles the visual representation of the data using `customtkinter` and `matplotlib`.

#### **Class: `Dashboard`**
*   **`__init__`**: Initializes the analytics engine and calls `setup_ui`.

#### **UI Structure (`setup_ui`)**
The dashboard uses a grid layout (4 rows):
1.  **Row 0 (Basic Stats):** "Total Members", "Pending Payments", "Active Check-ins", "Frozen".
    *   These use `create_stat_card` to show simple numbers.
2.  **Row 1 (Analytics):** "Retention Rate" (Green/Red based on >70%), "Expiring Soon".
3.  **Rows 2 & 3 (Graphs):** Complex charts embedded into the window.

#### **Graph Generation Methods:**
*   **`create_stat_card()`**: A helper method that creates a styled `CTkFrame` with a Title and Value label. It accepts a `text_color` argument to make numbers Green (good) or Red (bad).
*   **`create_revenue_forecast_graph()`**:
    *   Fetches data from `analytics.predict_revenue()`.
    *   Uses a **Bar Chart** to show "Predicted" vs "Guaranteed" revenue side-by-side.
    *   Embeds the `matplotlib` figure into Tkinter using `FigureCanvasTkAgg`.
*   **`create_trend_graph()`**:
    *   Uses a **Line Chart** with a shaded area (`fill_between`).
    *   Adds a dashed red line at 70% to show the "Target".
*   **`create_peak_hours_graph()`**:
    *   **Logic:** extract hour `dt.hour` from `attendance_log`.
    *   Uses `collections.Counter` to count check-ins per hour.
    *   Plots a smooth line graph showing busy times (e.g., 6 PM).
