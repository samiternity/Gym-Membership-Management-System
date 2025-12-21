# Team Roles and File Responsibilities

## Member 1 (SAMI): Dashboard, Analytics, Attendance & QA
**Files:**
- `src/ui/dashboard.py`: Main dashboard UI, charts, and KPI widgets.
- `src/analytics.py`: Business logic for calculating statistics (Retention, Revenue Forecasts).
- `src/ui/attendance.py`: Attendance tracking system (Check-in/Check-out).
- `src/styles.py`: Global design system (UI/UX), colors, and fonts.
- `src/app.py`: Main application container (UI/UX oversight).
- `Docs/Data Model.md`: Definition of JSON data structures.

## Member 2: Members & Trainers Modules
**Files:**
- `src/ui/members.py`: Member management (Add, Edit, Delete, Freeze).
- `src/ui/trainers.py`: Trainer management and assignment.
- `src/ui/visitors.py`: Visitor/Lead management (Potential members).
- `src/ui/payments.py`: Payment entry and history (Data entry for members).

## Member 3: Settings, Infrastructure & Security
**Files:**
- `src/ui/settings.py`: System configuration and backup controls.
- `src/auth_manager.py`: User authentication logic (Login/Logout).
- `src/ui/login.py`: Login window UI.
- `src/data_manager.py`: JSON file handling (Data Storage).
- `src/backup_manager.py`: Backup creation and restoration (Recovery).
- `src/utils.py` & `src/whatsapp_helper.py`: Backend helper functions.
