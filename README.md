DESIMS – Department Examination Management System

DESIMS is a web-based examination management system designed to simplify and automate examination planning and management at university departments.

The system helps department heads manage academic examination activities, including semester planning, examination scheduling, room allocation, invigilation assignments, conflict detection, and report generation.

Project Objectives

- Automate departmental examination planning.
- Simplify examination scheduling and management.
- Allocate examination rooms efficiently.
- Manage invigilator assignments.
- Detect scheduling and allocation conflicts.
- Generate useful examination management reports.
- Reduce manual work and errors associated with Word and Excel-based processes.

Technology Stack

Backend

- Python
- Django 5
- Django REST Framework
- SQLite (Development Database)

Frontend

- React
- TypeScript
- Vite
- Axios

Core Modules

Module| Description
Academics| Academic years, semesters, examination sessions, periods, and holidays
Semester Setup| Semester planning and course organization
Courses| Course management
Staff| Academic staff management
Rooms| Examination room management
Exams| Examination management
Scheduling| Examination timetable generation and management
Allocations| Examination room allocation
Invigilation| Invigilator assignment
Dashboard| Examination management overview and statistics
Conflicts| Scheduling and allocation conflict detection
Reports| Examination-related reports

Key Features

- Academic year and semester management.
- Semester-based course planning.
- Examination timetable management.
- Examination room allocation.
- Invigilator assignment.
- Scheduling conflict detection.
- Dashboard with examination statistics.
- Examination reports.

Project Structure

DESIMS/
├── backend/
│   ├── academics/
│   ├── semester_setup/
│   ├── courses/
│   ├── staff/
│   ├── rooms/
│   ├── exams/
│   ├── scheduling/
│   ├── allocations/
│   ├── invigilation/
│   ├── dashboard/
│   ├── conflicts/
│   └── reports/
│
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── services/
    │   └── ...
    └── ...

Note: The directory structure is illustrative; adjust it to match the actual repository layout.

Development Status

DESIMS is actively under development.

Current development focus:

- Backend API development.
- React frontend integration.
- Dashboard and navigation.
- Examination scheduling and management workflows.

Future Improvements

- Automated examination timetable generation.
- Advanced room and invigilator allocation.
- More comprehensive conflict detection.
- Improved reporting and export capabilities.
- Enhanced user and role management.

Author

Developed as a university departmental examination management solution.

---

DESIMS – Making Examination Management More Efficient.
