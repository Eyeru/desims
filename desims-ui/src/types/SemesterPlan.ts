
export interface SemesterPlan {
    id: number;
    academic_year_id: number;
    academic_year: string;
    year_level: number;
    semester: number;
    program_type: "REGULAR" | "EXTENSION";
    student_count: number;
    start_date: string;
    end_date: string;
    session_policy: "MORNING" | "AFTERNOON" | "MIXED";
    is_active: boolean;
    is_generated: boolean;
}

export interface CreateSemesterPlanData {
    academic_year_id: number;
    year_level: number;
    semester: number;
    program_type: "REGULAR" | "EXTENSION";
    student_count: number;
    start_date: string;
    end_date: string;
    session_policy: "MORNING" | "AFTERNOON" | "MIXED";
}
