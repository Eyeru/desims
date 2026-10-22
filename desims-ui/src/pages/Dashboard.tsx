import {useEffect, useState} from "react";
import API from "../services/api";
import Header from "../components/Header";
import SummaryCard from "../components/SummaryCard";
import type { DashboardResponse } from "../types/Dashboard";
import ActivePlanCard from "../components/ActivePlanCard";

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
            try {
                const response = await API.get("dashboard/");
                setDashboard(response.data);
            } catch (error) {
                console.error("Failed to load dashboard:", error);
            }
        }

        loadDashboard();
    }, []);

    return (
        <>
            <Header />

            <main className="dashboard">
                {dashboard.active_plan && (
                    <ActivePlanCard plan={dashboard.active_plan} />
    )}

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