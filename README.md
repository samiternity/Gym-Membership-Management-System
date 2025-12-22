# Gymiternity - Gym Membership Management System

A modern, feature-rich GUI application for managing gym memberships, trainers, payments, and attendance tracking.

## Features

### Core Modules
- **Dashboard**: Real-time metrics, revenue forecasts, peak hours analysis (last 7 days), and active check-ins tracking
- **Member Management**: Add/Edit members, view profiles, manage memberships with freeze/unfreeze capabilities
- **Trainer Management**: Manage trainers with input validation, view assigned members via trainer profiles
- **Payment Management**: Track invoices with smart sorting (unpaid first by due date), mark payments as paid
- **Attendance Tracking**: Check-in/Check-out system with daily activity monitoring
- **Visitors**: Track leads, follow-ups, and convert visitors to members

### Additional Features
- **Authentication**: Secure login with case-insensitive usernames
- **Backup & Restore**: Automatic backups with easy restoration
- **Input Validation**: Form validation for members, trainers, and visitors
- **WhatsApp Integration**: Send messages directly via WhatsApp
- **Data Persistence**: All data saved to JSON files

## Installation

1. **Prerequisites**: Python 3.x

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python -m src.main
```

**Default Login**:
- Username: `admin`
- Password: `admin123`

## Project Structure

```
├── src/
│   ├── ui/                 # UI modules
│   │   ├── dashboard.py    # Dashboard with charts
│   │   ├── members.py      # Member management
│   │   ├── trainers.py     # Trainer management
│   │   ├── payments.py     # Payment tracking
│   │   ├── attendance.py   # Check-in/out system
│   │   ├── visitors.py     # Lead tracking
│   │   ├── settings.py     # Backup & account settings
│   │   └── login.py        # Authentication UI
│   ├── data_manager.py     # Data persistence
│   ├── auth_manager.py     # User authentication
│   ├── backup_manager.py   # Backup handling
│   ├── analytics.py        # Revenue & retention analytics
│   ├── app.py              # Main application
│   └── main.py             # Entry point
├── data/                   # JSON data files (auto-created)
└── requirements.txt        # Dependencies
```

## Technologies

- **Python 3.x**
- **CustomTkinter** - Modern UI framework
- **Matplotlib** - Dashboard charts and visualizations
- **Tkinter** - Native widgets (Treeview tables)

## Screenshots

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

## License

This project is for educational purposes.

## Contact

For any inquiries, please contact the repository owner.
