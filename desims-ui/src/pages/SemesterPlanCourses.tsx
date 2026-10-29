
import { useEffect, useState } from "react";
import API from "../services/api";
import type { SemesterPlan } from "../types/SemesterPlan";
import type { SemesterPlanCoursesResponse } from "../types/SemesterPlanCourses";

function SemesterPlanCourses() {
    const [plans, setPlans] = useState<SemesterPlan[]>([]);
    const [selectedPlanId, setSelectedPlanId] = useState("");
    const [result, setResult] =
        useState<SemesterPlanCoursesResponse | null>(null);
    const [loadingPlans, setLoadingPlans] = useState(true);
    const [loadingCourses, setLoadingCourses] = useState(false);
    const [error, setError] = useState("");

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
                    setSelectedPlanId(String(activePlan.id));
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
            setResult(null);
            return;
        }

        let cancelled = false;

        async function loadCourses() {
            try {
                setLoadingCourses(true);
                setError("");
                setResult(null);

                const response =
                    await API.get<SemesterPlanCoursesResponse>(
                        `semester-plans/${selectedPlanId}/courses/`
                    );

                if (!cancelled) {
                    setResult(response.data);
                }
            } catch {
                if (!cancelled) {
                    setError("Could not load courses for this plan.");
                }
            } finally {
                if (!cancelled) {
                    setLoadingCourses(false);
                }
            }
        }

        loadCourses();

        return () => {
            cancelled = true;
        };
    }, [selectedPlanId]);

    if (loadingPlans) {
        return <p>Loading semester plans...</p>;
    }

    return (
        <div className="page-container">
            <h1>Semester Plan Courses</h1>



            <p>
                Review the courses assigned to a semester plan before exam scheduling.
            </p>

            {plans.some((plan) => plan.is_active) ? (
                <p className="success-message">
                    The active semester plan is marked in the selection list.
                </p>
            ) : (
                <p className="error-message">
                    No semester plan is active. Activate a plan before preparing exams.
                </p>
            )}


            {plans.length === 0 ? (
                <p>Create a semester plan before viewing its courses.</p>
            ) : (
                <div className="form-container">
                    <label>
                        Semester Plan
                        <select
                            value={selectedPlanId}
                            onChange={(event) =>
                                setSelectedPlanId(event.target.value)
                            }
                        >
                            <option value="">Select a plan</option>

                            {plans.map((plan) => (
                                <option key={plan.id} value={plan.id}>
                                    {plan.academic_year} — Year {plan.year_level},
                                    Semester {plan.semester} — {plan.program_type}
                                    {plan.is_active ? " (Active)" : ""}
                                </option>
                            ))}
                        </select>
                    </label>
                </div>
            )}

            {error && <p className="error-message">{error}</p>}

            {loadingCourses && <p>Loading courses...</p>}

            {result && (
                <>
                    <h2>
                        {result.academic_year} — Year {result.year_level},
                        Semester {result.semester}
                    </h2>

                    <p>
                        Program: {result.program_type} | Total matching courses:{" "}
                        {result.course_count}
                    </p>

                    <p>
                        {result.course_count > 0
                            ? "Courses loaded successfully. Review the list below before proceeding to exam scheduling."
                            : "No matching courses found. Add or correct the course records before proceeding."}
                    </p>

                    {result.courses.length === 0 ? (
                        <p>
                            No courses match this plan yet. Check the course
                            records for the correct year, semester, and program.
                        </p>
                    ) : (
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Course Code</th>
                                        <th>Course Title</th>
                                        <th>Year Level</th>
                                        <th>Semester</th>
                                        <th>Program</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {result.courses.map((course) => (
                                        <tr key={course.id}>
                                            <td>{course.code}</td>
                                            <td>{course.title}</td>
                                            <td>{course.year_level}</td>
                                            <td>{course.semester}</td>
                                            <td>{course.program_type}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default SemesterPlanCourses;
