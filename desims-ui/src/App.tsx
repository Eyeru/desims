import { Navigate, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import PlaceholderPage from "./pages/PlaceholderPage";
import AcademicYears from "./pages/AcademicYears";
import SemesterPlans from "./pages/SemesterPlans";
import SemesterPlanCourses from "./pages/SemesterPlanCourses";
import Courses from "./pages/Courses";
import "./App.css";

function App() {
  return (
        <Routes>
            <Route path="*" element={<Navigate to="/" replace />} />
            <Route path="/academic-years" element={
                <AcademicYears />} />
            <Route path="/semester-plans" element={
                <SemesterPlans />} />
            <Route path="/courses" element={<Courses />} />
            <Route path="/rooms" element={
                <PlaceholderPage title="Rooms" />} /> 
            <Route path="/staff" element={
                <PlaceholderPage title="Staff" />} />
            <Route path="/exam-schedules" element={
                <PlaceholderPage title="Exam schedules" />} />
            <Route path="/reports" element={
                <PlaceholderPage title="Reports" />} />
            <Route path="/semester-plan-courses" element={<SemesterPlanCourses />}/>
            <Route path="/" element={<Dashboard />} />
        </Routes>
    );
}

export default App;