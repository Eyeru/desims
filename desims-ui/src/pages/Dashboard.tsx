import Header from "../components/Header";

function Dashboard() {
    return (
        <>
            <Header />

            <main className="dashboard">
                <h2>Exam Planning</h2>

                <div className="card">
                    <p>
                        <strong>Academic Year:</strong> 2025/2026
                    </p>

                    <p>
                        <strong>Semester:</strong> First
                    </p>

                    <p>
                        <strong>Program:</strong> Regular
                    </p>

                    <button>Create Exam Plan</button>
                </div>
            </main>
        </>
    );
}

export default Dashboard;