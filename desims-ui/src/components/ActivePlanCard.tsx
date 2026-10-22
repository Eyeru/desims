
import type { ActivePlan } from "../types/Dashboard";

interface ActivePlanCardProps {
    plan: ActivePlan;
}

function ActivePlanCard({ plan }: ActivePlanCardProps) {
    return (
        <section className="active-plan-card">
            <h2>Active Examination Plan</h2>

            <div className="active-plan-details">
                <p>
                    <strong>Academic Year:</strong>{" "}
                    {plan.academic_year}
                </p>

                <p>
                    <strong>Year Level:</strong>{" "}
                    {plan.year_level}
                </p>

                <p>
                    <strong>Semester:</strong>{" "}
                    {plan.semester}
                </p>

                <p>
                    <strong>Program:</strong>{" "}
                    {plan.program_type === "REGULAR"
                        ? "Regular"
                        : plan.program_type}
                </p>

                <p>
                    <strong>Exam Session:</strong>{" "}
                    {plan.session_policy === "MORNING"
                        ? "Morning only"
                        : plan.session_policy === "AFTERNOON"
                        ? "Afternoon only"
                        : plan.session_policy}
                </p>
            </div>
        </section>
    );
}

export default ActivePlanCard;
