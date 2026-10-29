
import { NavLink } from "react-router-dom";

function Header() {
    return (
        <header className="header">
            <div className="header-brand">
                <div className="header-logo">D</div>

                <div>
                    <h1>DESIMS</h1>
                    <p>Department Examination Management System</p>
                </div>
            </div>

            <nav className="navigation">
                <NavLink to="/" end className="nav-link">
                    Dashboard
                </NavLink>

                <NavLink to="/academic-years" className="nav-link">
                    Academic Years
                </NavLink>

                <NavLink to="/semester-plans" className="nav-link">
                    Semester Plans
                </NavLink>

                <NavLink to="/courses" className="nav-link">
                    Courses
                </NavLink>

                <NavLink to="/rooms" className="nav-link">
                    Rooms
                </NavLink>

                <NavLink to="/staff" className="nav-link">
                    Staff
                </NavLink>

                <NavLink to="/exam-schedules" className="nav-link">
                    Exam Schedules
                </NavLink>

                <NavLink to="/reports" className="nav-link">
                    Reports
                </NavLink>
                <NavLink to="/semester-plan-courses">
                    Plan Courses
                </NavLink>
            </nav>
        </header>
    );
}

export default Header;
