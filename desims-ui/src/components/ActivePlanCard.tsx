
import type { ActivePlan } from "../types/Dashboard";

interface ActivePlanCardProps {
    plan: ActivePlan;
}

function ActivePlanCard({ plan }: ActivePlanCardProps) {
    const program =
        plan.program_type === "REGULAR"
            ? "Regular"
            : plan.program_type === "EXTENSION"
            ? "Extension"
            : plan.program_type;

    const session =
        plan.session_policy === "MORNING"
            ? "Morning only"
            : plan.session_policy === "AFTERNOON"
            ? "Afternoon only"
            : "Mixed sessions";

    return (
        <section className="active-plan-card">
            <div className="active-plan-header">
                <div>
                    <p className="active-plan-eyebrow">
                        CURRENT CONFIGURATION
                    </p>
                    <h2>Active Examination Plan</h2>
                    <p className="active-plan-description">
                        Exam planning details for the selected cohort.
                    </p>
                </div>

                <span className="active-plan-status">
                    Active
                </span>
            </div>

            <div className="active-plan-details">
                <div className="plan-detail">
                    <span className="plan-detail-label">
                        Academic Year
                    </span>
                    <strong>{plan.academic_year}</strong>
                </div>

                <div className="plan-detail">
                    <span className="plan-detail-label">
                        Year Level
                    </span>
                    <strong>Year {plan.year_level}</strong>
                </div>

                <div className="plan-detail">
                    <span className="plan-detail-label">
                        Semester
                    </span>
                    <strong>Semester {plan.semester}</strong>
                </div>

                <div className="plan-detail">
                    <span className="plan-detail-label">
                        Program
                    </span>
                    <strong>{program}</strong>
                </div>

                <div className="plan-detail">
                    <span className="plan-detail-label">
                        Exam Session
                    </span>
                    <strong>{session}</strong>
                </div>
            </div>
        </section>
    );
}

export default ActivePlanCard;
