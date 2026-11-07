
import { useEffect, useState } from "react";
import API from "../services/api";
import type { SemesterPlan } from "../types/SemesterPlan";
import type { SemesterPlanCoursesResponse } from "../types/SemesterPlanCourses";
import Header from "../components/Header";
type InvigilationAssignment = {
    id: number;
    staff_id: number;
    staff_name: string;
    is_auto: boolean;
};

type InvigilationSchedule = {
    schedule_id: number;
    exam_code: string;
    exam_title: string;
    date: string;
    session: string;
    student_count: number;
    rooms: {
        id: number;
        name: string;
        building: string;
        room_type: string;
        allocated_students: number;
    }[];
    required_invigilators: number;
    assigned_invigilators: InvigilationAssignment[];
    assigned_count: number;
    remaining_count: number;
};

type InvigilationResponse = {
    plan_id: number;
    program_type: string;
    is_active: boolean;
    scheduled_count: number;
    schedules: InvigilationSchedule[];
};

type InvigilationBatchResponse = {
    plan_id: number;
    summary: {
        success_count: number;
        skipped_count: number;
        failed_count: number;
    };
    results: {
        schedule_id: number;
        exam_code: string;
        status: "success" | "skipped" | "failed";
        message: string;
        assignments: InvigilationAssignment[];
    }[];
    message: string;
};

function SemesterPlanCourses() {
    const [plans, setPlans] = useState<SemesterPlan[]>([]);
    const [selectedPlanId, setSelectedPlanId] = useState("");
    const [result, setResult] =
        useState<SemesterPlanCoursesResponse | null>(null);
    const [loadingPlans, setLoadingPlans] = useState(true);
    const [loadingCourses, setLoadingCourses] = useState(false);
    const [generatingExams, setGeneratingExams] = useState(false);
    const [generationMessage, setGenerationMessage] = useState("");
    const [generatingSchedule, setGeneratingSchedule] = useState(false);
    const [scheduleMessage, setScheduleMessage] = useState("");
    const [scheduleResult, setScheduleResult] = useState<any>(null);
    const [error, setError] = useState("");
    const [allocatingRooms, setAllocatingRooms] = useState(false);
    const [allocationResult, setAllocationResult] = useState<any>(null);
    const [allocationMessage, setAllocationMessage] = useState("");
    const [invigilationData, setInvigilationData] =
    useState<InvigilationResponse | null>(null);

    const [assigningAllInvigilators, setAssigningAllInvigilators] =
        useState(false);

    const [invigilationMessage, setInvigilationMessage] =
        useState("");

    const [invigilationResult, setInvigilationResult] =
        useState<InvigilationBatchResponse | null>(null);

    const generateExams = async () => {
        if (!selectedPlanId || !result || result.course_count === 0) {
            return;
        }

        try {
            setGeneratingExams(true);
            setError("");
            setGenerationMessage("");

            const response = await API.post(
                `semester-plans/${selectedPlanId}/generate-exams/`,
                {}
            );

            setGenerationMessage(response.data.message);
        } catch (err: unknown) {
            if (
                typeof err === "object" &&
                err !== null &&
                "response" in err
            ) {
                setError("Could not generate exams. Check the server response.");
            } else {
                setError("Could not connect to the server. Check that Django is running.");
            }
        } finally {
            setGeneratingExams(false);
        }
    };


    const generateSchedule = async () => {
            if (!selectedPlanId) {
                return;
            }

            try {
                setGeneratingSchedule(true);
                setError("");
                setScheduleMessage("");
                setScheduleResult(null);

                const response = await API.post(
                    `semester-plans/${selectedPlanId}/generate-schedule/`,
                    {}
                );

                setScheduleResult(response.data);
                setScheduleMessage(response.data.message);
            } catch (err: unknown) {
                if (
                    typeof err === "object" &&
                    err !== null &&
                    "response" in err
                ) {
                    setError(
                        "Could not generate the schedule. The plan may already have schedules, or the server returned a validation error."
                    );
                } else {
                    setError(
                        "Could not connect to the server. Check that Django is running."
                    );
                }
            } finally {
                setGeneratingSchedule(false);
            }
        };

    const allocateRooms = async () => {
        if (!selectedPlanId || !scheduleResult) {
            return;
        }

        try {
            setAllocatingRooms(true);
            setError("");
            setAllocationMessage("");
            setAllocationResult(null);

            const response = await API.post(
                `semester-plans/${selectedPlanId}/allocate-rooms/`,
                {}
            );

            setAllocationResult(response.data.data);
            setAllocationMessage(response.data.message);
            // Refresh room and invigilation data after allocation
            await loadInvigilation();
        } catch (err: unknown) {
            if (
                typeof err === "object" &&
                err !== null &&
                "response" in err
            ) {
                setError(
                    "Room allocation failed. Check the server response."
                );
            } else {
                setError(
                    "Could not connect to the server. Check that Django is running."
                );
            }
        } finally {
            setAllocatingRooms(false);
        }
    };

    const loadInvigilation = async () => {
        if (!selectedPlanId) {
            return;
        }

        try {
            const response = await API.get<InvigilationResponse>(
                `semester-plans/${selectedPlanId}/invigilation/`
            );

            setInvigilationData(response.data);
        } catch {
            setError("Could not load invigilation data.");
        }
    };

    const assignAllInvigilators = async () => {
        if (!selectedPlanId || !invigilationData) {
            return;
        }

        try {
            setAssigningAllInvigilators(true);
            setError("");
            setInvigilationMessage("");
            setInvigilationResult(null);

            const response = await API.post<InvigilationBatchResponse>(
                `semester-plans/${selectedPlanId}/assign-invigilators/`,
                {}
            );

            setInvigilationResult(response.data);
            setInvigilationMessage(response.data.message);

            await loadInvigilation();
        } catch {
            setError("Batch invigilation assignment failed.");
        } finally {
            setAssigningAllInvigilators(false);
        }
    };

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
            setScheduleResult(null);
            setScheduleMessage("");
            setAllocationResult(null);
            setAllocationMessage("");
            setInvigilationData(null);
            setInvigilationMessage("");
            setInvigilationResult(null);
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
                    const scheduleResponse = await API.get(
                        `semester-plans/${selectedPlanId}/schedule/`
                    );

                    if (!cancelled && scheduleResponse.data.scheduled_count > 0) {
                        setScheduleResult(scheduleResponse.data);
                        setScheduleMessage(
                            `${scheduleResponse.data.scheduled_count} saved exam(s) loaded.`
                        );
                    }

                    if (!cancelled && scheduleResponse.data.scheduled_count > 0) {
                        const invigilationResponse =
                            await API.get<InvigilationResponse>(
                                `semester-plans/${selectedPlanId}/invigilation/`
                            );

                        if (!cancelled) {
                            setInvigilationData(invigilationResponse.data);
                        }
                    }
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
        <>
            <Header />
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
                    <div className="form-container">
                        <button
                            type="button"
                            onClick={generateExams}
                            disabled={
                                generatingExams ||
                                loadingCourses ||
                                result.course_count === 0
                            }
                        >
                            {generatingExams ? "Generating Exams..." : "Generate Exams"}
                        </button>
                        <button
                            type="button"
                            onClick={generateSchedule}
                            disabled={
                                generatingSchedule ||
                                generatingExams ||
                                loadingCourses ||
                                result.course_count === 0
                            }
                        >
                            {generatingSchedule
                                ? "Generating Schedule..."
                                : "Generate Schedule"}
                        </button>

                        <button
                            type="button"
                            onClick={allocateRooms}
                            disabled={
                                allocatingRooms ||
                                generatingSchedule ||
                                generatingExams ||
                                loadingCourses ||
                                !scheduleResult
                            }
                        >
                            {allocatingRooms
                                ? "Allocating Rooms..."
                                : "Allocate All Rooms"}
                        </button>

                        <button
                            type="button"
                            onClick={assignAllInvigilators}
                            disabled={
                                assigningAllInvigilators ||
                                allocatingRooms ||
                                generatingSchedule ||
                                generatingExams ||
                                !invigilationData ||
                                !invigilationData.is_active ||
                                invigilationData.scheduled_count === 0 ||
                                invigilationData.schedules.some(
                                    (schedule) => schedule.rooms.length === 0
                                )
                            }
                        >
                            {assigningAllInvigilators
                                ? "Assigning Invigilators..."
                                : "Assign All Invigilators"}
                        </button>

                        {generationMessage && (
                            <p className="success-message">
                                {generationMessage}
                            </p>
                        )}

                        {scheduleMessage && (
                            <p className="success-message">
                                {scheduleMessage}
                            </p>
                        )}
                        {allocationMessage && (
                            <p className="success-message">
                                {allocationMessage}
                            </p>
                        )}
                        
                        {invigilationMessage && (
                            <p className="success-message">
                                {invigilationMessage}
                            </p>
                        )}

                        <p>
                            {result.course_count > 0
                                ? "Review the examination preparation progress for each course below."
                                : "No matching courses found. Add or correct the course records before proceeding."}
                        </p>

                        {result.courses.length === 0 ? (
                            <p>
                                No courses match this plan yet. Check the course
                                records for the correct year, semester, and program.
                            </p>
                        ) : (
                            <div className="table-container">
                                <h3>Course Preparation Progress</h3>

                                <table>
                                    <thead>
                                        <tr>
                                            <th>Course</th>
                                            <th>Exam Schedule</th>
                                            <th>Room Allocation</th>
                                            <th>Invigilation</th>
                                        </tr>
                                    </thead>

                                    <tbody>
                                        {result.courses.map((course) => {
                                            const schedule = scheduleResult?.schedules?.find(
                                                (item: any) => item.exam_code === course.code
                                            );

                                            const invigilation = invigilationData?.schedules?.find(
                                                (item) => item.exam_code === course.code
                                            );

                                            return (
                                                <tr key={course.id}>
                                                    <td>
                                                        <strong>{course.code}</strong>
                                                        <br />
                                                        {course.title}
                                                    </td>

                                                    <td>
                                                        {schedule ? (
                                                            <>
                                                                {schedule.date}
                                                                <br />
                                                                {schedule.session}
                                                            </>
                                                        ) : (
                                                            "Not scheduled"
                                                        )}
                                                    </td>

                                                    <td>
                                                        {!schedule
                                                            ? "—"
                                                            : !invigilation
                                                            ? "Loading details..."
                                                            : invigilation.rooms.length === 0
                                                                ? "Not allocated"
                                                                : invigilation.rooms.map(
                                                                    (room) => (
                                                                        <div key={room.id}>
                                                                            <strong>{room.name}</strong>
                                                                            <br />
                                                                            {room.building} — {room.room_type}
                                                                            <br />
                                                                            Students: {room.allocated_students}
                                                                        </div>
                                                                    )
                                                                )}
                                                    </td>

                                                    <td>
                                                        {!schedule
                                                            ? "—"
                                                            : !invigilation
                                                            ? "Loading details..."
                                                            : (
                                                                <>
                                                                    <strong>
                                                                        {invigilation.assigned_count}/
                                                                        {invigilation.required_invigilators}
                                                                    </strong>
                                                                    <br />
                                                                    {invigilation.assigned_invigilators
                                                                        .map((staff) => staff.staff_name)
                                                                        .join(", ") || "None assigned"}
                                                                </>
                                                            )}
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        )}

                        {invigilationMessage && (
                            <p className="success-message">
                                {invigilationMessage}
                            </p>
                        )}


                    </div>

                </>
            )}
        </div>
        </>
    );
}

export default SemesterPlanCourses;
