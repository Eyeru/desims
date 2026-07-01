import { useState, useEffect} from "react";
import API from "../services/api";
import Header from "../components/Header";
import SummaryCard from "../components/SummaryCard";
import { DashboardResponse } from "../types/Dashboard";

function Dashboard() {
    const [dashboard, setDashboard] = useState<DashboardResponse>({
    active_plan: null,
    statistics: {
        courses: 0,
        rooms: 0,
        staff: 0,
        schedules: 0,
    },
    });
    useEffect(() => {

        async function loadDashboard() {

            const response = await API.get("dashboard/");

            setDashboard(response.data);

        }

        loadDashboard();

    }, []);

    return (
        <>
            <Header />

            <main className="dashboard">

                <SummaryCard
                    title="Courses"
                    value={dashboard.statistics.courses}
                />

                <SummaryCard
                    title="Schedules"
                    value={dashboard.statistics.schedules}
                />

                <SummaryCard
                    title="Rooms"
                    value={dashboard.statistics.rooms}
                />

                <SummaryCard
                    title="Invigilators"
                    value={dashboard.statistics.staff}
                />

            </main>
        </>
    );
}

export default Dashboard;