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

## Screenshots

Here are some glimpses of the application:

| Dashboard | Member Management |
|:---:|:---:|
| ![Dashboard](Pics/Screenshot%202025-11-22%20172728.png) | ![Member Management](Pics/Screenshot%202025-11-22%20172804.png) |

| Trainer Management | Payment Management |
|:---:|:---:|
| ![Trainer Management](Pics/Screenshot%202025-11-22%20172855.png) | ![Payment Management](Pics/Screenshot%202025-11-22%20172920.png) |

| Attendance Tracking | Analytics |
|:---:|:---:|
| ![Attendance](Pics/Screenshot%202025-11-22%20172938.png) | ![Analytics](Pics/Screenshot%202025-11-22%20172954.png) |

| User Profile | Settings |
|:---:|:---:|
| ![Profile](Pics/Screenshot%202025-11-22%20173008.png) | ![Settings](Pics/Screenshot%202025-11-22%20173038.png) |

## Contact
For any inquiries, please contact the repository owner.

