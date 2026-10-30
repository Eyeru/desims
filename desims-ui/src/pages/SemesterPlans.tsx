
import { useEffect, useState } from "react";
import API from "../services/api";
import type { SemesterPlan, CreateSemesterPlanData } from "../types/SemesterPlan";
import type { AcademicYear } from "../types/AcademicYear";
import Header from "../components/Header";

function SemesterPlans() {
    const [plans, setPlans] = useState<SemesterPlan[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    
    const [academicYears, setAcademicYears] = useState<AcademicYear[]>([]);
    const [saving, setSaving] = useState(false);
    const [success, setSuccess] = useState("");
    const [formError, setFormError] = useState("");
    const [activatingId, setActivatingId] = useState<number | null>(null);
    const [form, setForm] = useState<CreateSemesterPlanData>({
        academic_year_id: 0,
        year_level: 1,
        semester: 1,
        program_type: "REGULAR",
        student_count: 1,
        start_date: "",
        end_date: "",
        session_policy: "MIXED",
    });


    async function loadPlans() {
        
        try {
            setLoading(true);
            setError("");

            const response = await API.get<SemesterPlan[]>(
                "semester-plans/"
            );

            setPlans(response.data);
        } catch {
            setError("Could not load semester plans. Please try again.");
        } finally {
            setLoading(false);
        }
    }

    async function loadAcademicYears() {
        try {
            const response = await API.get<AcademicYear[]>(
                "academic-years/"
            );

            setAcademicYears(response.data);

            const activeYear = response.data.find(
                (year) => year.is_active
            );

            if (activeYear) {
                setForm((current) => ({
                    ...current,
                    academic_year_id: activeYear.id,
                }));
            } else if (response.data.length > 0) {
                setForm((current) => ({
                    ...current,
                    academic_year_id: response.data[0].id,
                }));
            }
        } catch {
            setFormError("Could not load academic years.");
        }
    }

    
    async function handleCreatePlan(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();

        setSaving(true);
        setSuccess("");
        setFormError("");

        try {
            await API.post("semester-plans/create/", form);

            setSuccess("Semester plan created successfully.");

            setForm((current) => ({
                ...current,
                year_level: 1,
                semester: 1,
                program_type: "REGULAR",
                student_count: 1,
                start_date: "",
                end_date: "",
                session_policy: "MIXED",
            }));

            await loadPlans();
        } catch (error: unknown) {
            if (
                typeof error === "object" &&
                error !== null &&
                "response" in error
            ) {
                const apiError = error as {
                    response?: {
                        data?: {
                            error?: string;
                        };
                    };
                };

                setFormError(
                    apiError.response?.data?.error ??
                    "Could not create semester plan."
                );
            } else {
                setFormError("Could not create semester plan.");
            }
        } finally {
            setSaving(false);
        }
    }

    async function handleActivatePlan(planId: number) {
        setActivatingId(planId);
        setError("");
        setSuccess("");
        setFormError("");

        try {
            await API.post(`semester-plans/${planId}/activate/`);

            setSuccess("Semester plan activated successfully.");

            await loadPlans();
        } catch {
            setFormError("Could not activate the semester plan. Please try again.");
        } finally {
            setActivatingId(null);
        }
    }
    useEffect(() => {
        loadPlans();
        loadAcademicYears();
    }, []);

    if (loading) {
        return <p>Loading semester plans...</p>;
    }

    return (
        <>
            <Header />

            <main className="page-container">
            <h1>Semester Plans</h1>

            <form onSubmit={handleCreatePlan} className="form-container">
                <h2>Create Semester Plan</h2>

                {formError && (
                    <p className="error-message">{formError}</p>
                )}

                {success && (
                    <p className="success-message">{success}</p>
                )}

                {academicYears.length === 0 ? (
                    <p>
                        Please create an academic year before creating a semester plan.
                    </p>
                ) : (
                    <>
                        <label>
                            Academic Year
                            <select
                                value={form.academic_year_id}
                                onChange={(event) =>
                                    setForm({
                                        ...form,
                                        academic_year_id: Number(event.target.value),
                                    })
                                }
                                required
                            >
                                {academicYears.map((year) => (
                                    <option key={year.id} value={year.id}>
                                        {year.name}
                                        {year.is_active ? " (Active)" : ""}
                                    </option>
                                ))}
                            </select>
                        </label>

                        <label>
                            Year Level
                            <select
                                value={form.year_level}
                                onChange={(event) =>
                                    setForm({
                                        ...form,
                                        year_level: Number(event.target.value),
                                    })
                                }
                            >
                                {[1, 2, 3, 4, 5].map((level) => (
                                    <option key={level} value={level}>
                                        Year {level}
                                    </option>
                                ))}
                            </select>
                        </label>

                        <label>
                            Semester
                            <select
                                value={form.semester}
                                onChange={(event) =>
                                    setForm({
                                        ...form,
                                        semester: Number(event.target.value),
                                    })
                                }
                            >
                                <option value={1}>Semester 1</option>
                                <option value={2}>Semester 2</option>
                            </select>
                        </label>

                        <label>
                            Program Type
                            <select
                                value={form.program_type}
                                onChange={(event) =>
                                    setForm({
                                        ...form,
                                        program_type: event.target.value as
                                            "REGULAR" | "EXTENSION",
                                    })
                                }
                            >
                                <option value="REGULAR">Regular</option>
                                <option value="EXTENSION">Extension</option>
                            </select>
                        </label>

                        <label>
                            Number of Students
                            <input
                                type="number"
                                min="1"
                                value={form.student_count}
                                onChange={(event) =>
                                    setForm({
                                        ...form,
                                        student_count: Number(event.target.value),
                                    })
                                }
                                required
                            />
                        </label>

                        <label>
                            Exam Period Start Date
                            <input
                                type="date"
                                value={form.start_date}
                                onChange={(event) =>
                                    setForm({
                                        ...form,
                                        start_date: event.target.value,
                                    })
                                }
                                required
                            />
                        </label>

                        <label>
                            Exam Period End Date
                            <input
                                type="date"
                                value={form.end_date}
                                onChange={(event) =>
                                    setForm({
                                        ...form,
                                        end_date: event.target.value,
                                    })
                                }
                                min={form.start_date || undefined}
                                required
                            />
                        </label>

                        <label>
                            Exam Session Policy
                            <select
                                value={form.session_policy}
                                onChange={(event) =>
                                    setForm({
                                        ...form,
                                        session_policy: event.target.value as
                                            "MORNING" | "AFTERNOON" | "MIXED",
                                    })
                                }
                            >
                                <option value="MORNING">Morning only</option>
                                <option value="AFTERNOON">Afternoon only</option>
                                <option value="MIXED">Morning and afternoon</option>
                            </select>
                        </label>

                        <button type="submit" disabled={saving}>
                            {saving ? "Creating..." : "Create Semester Plan"}
                        </button>
                    </>
                )}
            </form>

            {error && <p className="error-message">{error}</p>}

            {!error && plans.length === 0 && (
                <p>No semester plans found.</p>
            )}

            {plans.length > 0 && (
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Academic Year</th>
                                <th>Year Level</th>
                                <th>Semester</th>
                                <th>Program</th>
                                <th>Students</th>
                                <th>Exam Period</th>
                                <th>Session</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>

                        <tbody>
                            {plans.map((plan) => (
                                <tr key={plan.id}>
                                    <td>{plan.academic_year}</td>
                                    <td>{plan.year_level}</td>
                                    <td>{plan.semester}</td>
                                    <td>{plan.program_type}</td>
                                    <td>{plan.student_count}</td>
                                    <td>
                                        {plan.start_date} – {plan.end_date}
                                    </td>
                                    <td>{plan.session_policy}</td>
                                    <td>
                                        {plan.is_active ? "Active" : "Inactive"}
                                    </td>
                                    <td>
                                        {plan.is_active ? (
                                            <span>Currently Active</span>
                                        ) : (
                                            <button
                                                type="button"
                                                onClick={() => handleActivatePlan(plan.id)}
                                                disabled={activatingId !== null}
                                            >
                                                {activatingId === plan.id
                                                    ? "Activating..."
                                                    : "Activate"}
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
            </main>
        </>
    );
}

export default SemesterPlans;
