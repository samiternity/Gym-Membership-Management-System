# Gym Membership Management System

A GUI-based application for managing gym memberships, trainers, payments, and attendance.

## Features
-   **Dashboard**: Overview of key metrics and charts.
-   **Member Management**: Add/Edit members, view profiles, manage memberships.
-   **Trainer Management**: Manage trainers and their fees.
-   **Payment Management**: Track invoices and mark payments.
-   **Attendance Tracking**: Check-in/Check-out system.
-   **Visitors**: Track leads and convert them to members.
-   **Data Persistence**: All data is saved to JSON files in the `data/` directory.

## Installation

1.  Install Python 3.x.
2.  Install dependencies:
    ```bash
    pip install customtkinter matplotlib packaging
    ```

## Usage

Run the application:
```bash
python src/main.py
```

## Project Structure
-   `src/`: Source code.
    -   `ui/`: UI modules (Dashboard, Members, etc.).
    -   `data_manager.py`: Handles data loading/saving.
    -   `app.py`: Main application class.
-   `data/`: JSON data files (created automatically).
