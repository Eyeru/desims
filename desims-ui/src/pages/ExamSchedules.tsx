
import { useEffect, useState } from "react";
import API from "../services/api";
import type { SemesterPlan } from "../types/SemesterPlan";
import Header from "../components/Header";

type ExamSchedule = {
    id: number;
    exam_code: string;
    exam_title: string;
    date: string;
    session: string;
    is_auto: boolean;
    is_final: boolean;
};

type ScheduleResponse = {
    plan_id: number;
    scheduled_count: number;
    schedules: ExamSchedule[];
};

function ExamSchedules() {
    const [plans, setPlans] = useState<SemesterPlan[]>([]);
    const [selectedPlanId, setSelectedPlanId] = useState<number>(0);
    const [scheduleData, setScheduleData] =
        useState<ScheduleResponse | null>(null);

    const [loadingPlans, setLoadingPlans] = useState(true);
    const [loadingSchedules, setLoadingSchedules] = useState(false);
    const [error, setError] = useState("");
    const [finalizing, setFinalizing] = useState(false);
    const [successMessage, setSuccessMessage] = useState("");

    useEffect(() => {
        async function loadPlans() {
            try {
                const response = await API.get<SemesterPlan[]>(
                    "semester-plans/"
                );

                setPlans(response.data);

                const activePlan = response.data.find(
                    (plan) => plan.is_active
                );

                if (activePlan) {
                    setSelectedPlanId(activePlan.id);
                } else if (response.data.length > 0) {
                    setSelectedPlanId(response.data[0].id);
                }
            } catch {
                setError("Could not load semester plans.");
            } finally {
                setLoadingPlans(false);
            }
        }

        loadPlans();
    }, []);

    useEffect(() => {
        if (!selectedPlanId) {
            setScheduleData(null);
            return;
        }

        async function loadSchedules() {
            try {
                setLoadingSchedules(true);
                setError("");
                setScheduleData(null);

                const response = await API.get<ScheduleResponse>(
                    `semester-plans/${selectedPlanId}/schedule/`
                );

                setScheduleData(response.data);
            } catch {
                setError("Could not load exam schedules. Please try again.");
            } finally {
                setLoadingSchedules(false);
            }
        }

        loadSchedules();
    }, [selectedPlanId]);

    const selectedPlan = plans.find(
        (plan) => plan.id === selectedPlanId
    );
    async function handleFinalizeSchedule() {
        if (!selectedPlanId || !scheduleData) return;

        const confirmed = window.confirm(
            "Are you sure you want to finalize this examination timetable? " +
            "Please make sure you have reviewed all scheduled exams."
        );

        if (!confirmed) return;

        try {
            setFinalizing(true);
            setError("");
            setSuccessMessage("");

            await API.post(
                `semester-plans/${selectedPlanId}/finalize-schedule/`
            );

            const response = await API.get<ScheduleResponse>(
                `semester-plans/${selectedPlanId}/schedule/`
            );

            setScheduleData(response.data);
            setSuccessMessage(
                "Examination timetable finalized successfully."
            );
        } catch {
            setError("Could not finalize the examination timetable.");
        } finally {
            setFinalizing(false);
        }
    }
    if (loadingPlans) {
        return <p>Loading semester plans...</p>;
    }

    return (
        <>
            <Header />

            <main className="page-container">
                <h1>Exam Schedules</h1>

                <p>
                    View the examination timetable for a selected semester plan.
                </p>

                {plans.length === 0 ? (
                    <p>No semester plans found. Create a semester plan first.</p>
                ) : (
                    <>
                        <div className="form-container">
                            <label>
                                Select Semester Plan

                                <select
                                    value={selectedPlanId}
                                    onChange={(event) =>
                                        setSelectedPlanId(
                                            Number(event.target.value)
                                        )
                                    }
                                >
                                    {plans.map((plan) => (
                                        <option key={plan.id} value={plan.id}>
                                            {plan.academic_year} | Year{" "}
                                            {plan.year_level} | Semester{" "}
                                            {plan.semester} | {plan.program_type}
                                            {plan.is_active ? " (Active)" : ""}
                                        </option>
                                    ))}
                                </select>
                            </label>
                        </div>

                        {selectedPlan && (
                            <div className="form-container">
                                <h2>Selected Plan</h2>

                                <p>
                                    <strong>Academic Year:</strong>{" "}
                                    {selectedPlan.academic_year}
                                </p>

                                <p>
                                    <strong>Program:</strong>{" "}
                                    {selectedPlan.program_type}
                                </p>

                                <p>
                                    <strong>Year Level:</strong>{" "}
                                    {selectedPlan.year_level}
                                </p>

                                <p>
                                    <strong>Semester:</strong>{" "}
                                    {selectedPlan.semester}
                                </p>
                            </div>
                        )}

                        {error && (
                            <p className="error-message">{error}</p>
                        )}

                        {loadingSchedules && (
                            <p>Loading exam schedules...</p>
                        )}

                        {!loadingSchedules &&
                            !error &&
                            scheduleData &&
                            scheduleData.scheduled_count === 0 && (
                                <p>
                                    No exam schedules found for this semester plan.
                                </p>
                            )}

                        {!loadingSchedules &&
                            !error &&
                            scheduleData &&
                            scheduleData.scheduled_count > 0 && (
                                <>
                                    <h2>
                                        Scheduled Exams (
                                        {scheduleData.scheduled_count})
                                    </h2>
                                    {successMessage && (
                                        <p className="success-message">{successMessage}</p>
                                    )}

                                    <div className="form-actions">
                                        <button
                                            type="button"
                                            onClick={handleFinalizeSchedule}
                                            disabled={
                                                finalizing ||
                                                scheduleData.schedules.every(
                                                    (schedule) => schedule.is_final
                                                )
                                            }
                                        >
                                            {finalizing
                                                ? "Finalizing..."
                                                : scheduleData.schedules.every(
                                                    (schedule) => schedule.is_final
                                                )
                                                ? "Timetable Finalized"
                                                : "Finalize Timetable"}
                                        </button>
                                    </div>

                                    <div className="table-container">
                                        <table>
                                            <thead>
                                                <tr>
                                                    <th>S.N</th>
                                                    <th>Course Code</th>
                                                    <th>Course Title</th>
                                                    <th>Exam Date</th>
                                                    <th>Session</th>
                                                    <th>Schedule Type</th>
                                                    <th>Status</th>
                                                </tr>
                                            </thead>

                                            <tbody>
                                                {scheduleData.schedules.map(
                                                    (schedule, index) => (
                                                        <tr key={schedule.id}>
                                                            <td>{index + 1}</td>
                                                            <td>{schedule.exam_code}</td>
                                                            <td>{schedule.exam_title}</td>
                                                            <td>{schedule.date}</td>
                                                            <td>{schedule.session}</td>
                                                            <td>
                                                                {schedule.is_auto
                                                                    ? "Automatic"
                                                                    : "Manual"}
                                                            </td>
                                                            <td>
                                                                {schedule.is_final
                                                                    ? "Finalized"
                                                                    : "Not finalized"}
                                                            </td>
                                                        </tr>
                                                    )
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                </>
                            )}
                    </>
                )}
            </main>
        </>
    );
}

export default ExamSchedules;
