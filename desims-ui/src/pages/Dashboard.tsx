import { useState } from "react";
import Header from "../components/Header";
import SummaryCard from "../components/SummaryCard";

function Dashboard() {
    const [courses, setCourses] = useState(6);

    return (
        <>
            <Header />

            <main className="dashboard">

                <SummaryCard
                    title="Courses"
                    value={courses}
                />
                <button
                    onClick={() => setCourses(courses + 1)}>
                    Add Course
                </button>

                <SummaryCard
                    title="Schedules"
                    value={6}
                />

                <SummaryCard
                    title="Rooms"
                    value={8}
                />

                <SummaryCard
                    title="Invigilators"
                    value={12}
                />

            </main>
        </>
    );
}

export default Dashboard;