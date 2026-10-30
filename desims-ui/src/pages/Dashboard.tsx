
import { useEffect, useState } from "react";
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

    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadDashboard() {
            try {
                const response = await API.get("dashboard/");
                setDashboard(response.data);
            } catch (error) {
                console.error("Failed to load dashboard:", error);
            } finally {
                setLoading(false);
            }
        }

        loadDashboard();
    }, []);

    return (
        <>
            <Header />

            <main className="dashboard">
                <section className="dashboard-welcome">
                    <div>
                        <h1>Examination Management Dashboard</h1>
                        <p>
                            Monitor examination preparation and department
                            resources from one place.
                        </p>
                    </div>
                </section>

                <section className="dashboard-section">
                    <h2>Current Semester Plan</h2>

                    {loading ? (
                        <p>Loading active semester plan...</p>
                    ) : dashboard.active_plan ? (
                        <ActivePlanCard plan={dashboard.active_plan} />
                    ) : (
                        <p>
                            No active semester plan. Create or activate a
                            semester plan to begin examination preparation.
                        </p>
                    )}
                </section>

                <section className="dashboard-section">
                    <h2>Examination Overview</h2>

                    <div className="dashboard-summary-grid">
                        <SummaryCard
                            title="Courses"
                            value={dashboard.statistics.courses}
                        />

                        <SummaryCard
                            title="Scheduled Exams"
                            value={dashboard.statistics.schedules}
                        />
                    </div>
                </section>

                <section className="dashboard-section">
                    <h2>Department Resources</h2>

                    <div className="dashboard-summary-grid">
                        <SummaryCard
                            title="Rooms"
                            value={dashboard.statistics.rooms}
                        />

                        <SummaryCard
                            title="Academic Staff"
                            value={dashboard.statistics.staff}
                        />
                    </div>
                </section>
            </main>
        </>
    );
}

export default Dashboard;
