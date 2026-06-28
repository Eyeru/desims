import Header from "../components/Header";
import SummaryCard from "../components/SummaryCard";

function Dashboard() {
    return (
        <>
            <Header />

            <main className="dashboard">

                <SummaryCard
                    title="Courses"
                    value={6}
                />

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