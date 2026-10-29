
export interface PlanCourse {
    id: number;
    code: string;
    title: string;
    year_level: number;
    semester: number;
    program_type: "REGULAR" | "EXTENSION";
}

export interface SemesterPlanCoursesResponse {
    plan_id: number;
    academic_year: string;
    year_level: number;
    semester: number;
    program_type: "REGULAR" | "EXTENSION";
    course_count: number;
    courses: PlanCourse[];
}
