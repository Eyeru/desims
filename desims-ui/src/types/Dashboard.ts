export interface ActivePlan {
    academic_year: string;
    year_level: number;
    semester: number;
    program_type: string;
    session_policy: string;
}

export interface DashboardStats {
    courses: number;
    rooms: number;
    staff: number;
    schedules: number;
}

export interface DashboardResponse {
    active_plan: ActivePlan | null;
    statistics: DashboardStats;
}