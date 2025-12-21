# LLM Dataset Analysis Instructions

## Overview
You are provided with a synthetic dataset for a Gym Membership Management System. Your task is to analyze this data to verify the core analytics module's accuracy. This dataset includes member profiles, payment logs, membership history, attendance records, and visitor logs.

## Dataset Structure
The dataset consists of JSON files located in the `data/` directory (or generated via `generate_mock_data.py`).

### 1. `members.json`
*   **Key**: `member_id` (e.g., "M001")
*   **Fields**: `first_name`, `last_name`, `join_date`, `status` ("Active", "Inactive").

### 2. `membership_history.json`
*   **List of Records**: Each record represents a membership period.
*   **Key Fields**:
    *   `member_id`: Links to `members.json`.
    *   `plan_id`: Links to `plans.json`.
    *   `start_date` (YYYY-MM-DD): Start of the membership.
    *   `end_date` (YYYY-MM-DD): End of the membership.
    *   `status`: "Active", "Expired", or "Frozen".
    *   `freeze_history`: List of freeze periods (if any).

### 3. `payments_log.json`
*   **List of Records**: Financial transactions.
*   **Key Fields**:
    *   `amount_due`: Total cost (Plan + Trainer Fee).
    *   `amount_paid`: Actual amount paid.
    *   `status`: "Paid", "Unpaid", or "Pending".
    *   `payment_date`: Timestamp of payment.

### 4. `attendance_log.json`
*   **List of Records**: Gym visits.
*   **Key Fields**:
    *   `check_in_time`: ISO timestamp.
    *   `check_out_time`: ISO timestamp (or `null` if currently active).

---

## Analysis Tasks

Please perform the following calculations and provide a summary report.

### Task 1: Retention Metrics
**Goal**: Calculate the stability of the user base.
*   **Churn Rate Formula**:
    $$ \frac{\text{Members who expired in the last 30 days AND did not renew}}{\text{Total members active at the start of the period}} \times 100 $$
*   **Retention Rate Formula**: $100\% - \text{Churn Rate}$

*   **Logic**:
    1.  Identify members whose `end_date` falls in the last 30 days.
    2.  Check if they have a *subsequent* membership record starting on or after that `end_date`.
    3.  If no subsequent record exists, they churned.

### Task 2: Financial Metrics
**Goal**: Assess the gym's financial health.
*   **Lifetime Value (LTV)**:
    $$ \frac{\text{Total Revenue (Sum of 'amount_paid' where status='Paid')}}{\text{Total Unique Members}} $$
*   **Historical Revenue Trend**:
    *   Group `payments_log` by month (based on `payment_date`).
    *   Sum `amount_paid` for each month.

### Task 3: Operational Metrics
**Goal**: Identify immediate actions required.
*   **At-Risk Members**:
    *   List all `Active` members whose `end_date` is within the next 30 days.
*   **Peak Hours**:
    *   Parse `attendance_log` `check_in_time`.
    *   Count visits by hour of the day (0-23).
    *   Identify the hour with the highest frequency.

### Task 4: Prediction Verification
**Goal**: Verify the revenue forecast logic.
*   **Guaranteed Revenue**:
    *   Sum `amount_due` for any currently `Active` memberships that are marked `Unpaid`.
*   **Projected Revenue**:
    *   Calculate the average monthly revenue from the last 6 months.
    *   Combine with Guaranteed Revenue to estimate next month's earnings.

## Output Format
Please provide your analysis in the following format:
1.  **Metric Summary**: A table or bulleted list of the calculated values.
2.  **Observations**: Any anomalies or trends found in the generated data (e.g., "High churn rate in December").
3.  **Visualization Suggestions**: What charts would best represent this data (e.g., "Line chart for Revenue Trend").
