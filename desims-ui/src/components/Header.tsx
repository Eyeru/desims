
import { NavLink } from "react-router-dom";

function Header() {
    return (
        <header className="header">
            <div className="header-brand">
                <img
                    src="/uog-logo.png"
                    alt="University of Gondar logo"
                    className="header-logo"
                />

                <div className="header-brand-text">
                    <h1>DESIMS</h1>
                    <p>Department Examination Management System</p>
                    <span>University of Gondar | Computer Science</span>
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

                <NavLink to="/semester-plan-courses" className="nav-link">
                    Plan Courses
                </NavLink>
            </nav>
        </header>
    );
}

export default Header;
