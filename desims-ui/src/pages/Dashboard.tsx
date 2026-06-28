import { useState, useEffect} from "react";
import API from "../services/api";
import Header from "../components/Header";
import SummaryCard from "../components/SummaryCard";
import { DashboardStats } from "../types/Dashboard";

function Dashboard() {
    const [stats, setStats] = useState<DashboardStats>({
    courses: 0,
    rooms: 0,
    staff: 0,
    schedules: 0,
    });
    useEffect(() => {

        async function loadDashboard() {

            const response = await API.get("dashboard/");

            setStats(response.data);

        }

        loadDashboard();

    }, []);

    return (
        <>
            <Header />

            <main className="dashboard">

                <SummaryCard
                    title="Courses"
                    value={stats.courses}
                />

                <SummaryCard
                    title="Schedules"
                    value={stats.schedules}
                />

                <SummaryCard
                    title="Rooms"
                    value={stats.rooms}
                />

                <SummaryCard
                    title="Invigilators"
                    value={stats.staff}
                />

            </main>
        </>
    );
}

export default Dashboard;