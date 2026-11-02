
import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import API from "../services/api";
import Header from "../components/Header";

type ProgramType = "REGULAR" | "EXTENSION";

interface Course {
    id: number;
    code: string;
    title: string;
    year_level: number;
    semester: number;
    program_type: ProgramType;
    is_department_owned: boolean;
}

interface CourseForm {
    code: string;
    title: string;
    year_level: string;
    semester: string;
    program_type: ProgramType;
    is_department_owned: boolean;
}

const emptyForm: CourseForm = {
    code: "",
    title: "",
    year_level: "1",
    semester: "1",
    program_type: "REGULAR",
    is_department_owned: true,
};

function Courses() {
    const [courses, setCourses] = useState<Course[]>([]);
    const [form, setForm] = useState<CourseForm>(emptyForm);
    const [editingId, setEditingId] = useState<number | null>(null);

    const [search, setSearch] = useState("");
    const [yearFilter, setYearFilter] = useState("");
    const [semesterFilter, setSemesterFilter] = useState("");
    const [programFilter, setProgramFilter] = useState("");
    const [ownershipFilter, setOwnershipFilter] = useState("");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    function loadCourses() {
        setLoading(true);

        API.get<Course[]>("courses/")
            .then((response) => {
                setCourses(response.data);
                setError("");
            })
            .catch(() => {
                setError("Failed to load courses. Please try again.");
            })
            .finally(() => {
                setLoading(false);
            });
    }

    useEffect(() => {
        loadCourses();
    }, []);

    const filteredCourses = useMemo(() => {
        return courses.filter((course) => {
            const searchText = search.trim().toLowerCase();

            const matchesSearch =
                !searchText ||
                course.code.toLowerCase().includes(searchText) ||
                course.title.toLowerCase().includes(searchText);

            const matchesYear =
                !yearFilter ||
                course.year_level.toString() === yearFilter;

            const matchesSemester =
                !semesterFilter ||
                course.semester.toString() === semesterFilter;

            const matchesProgram =
                !programFilter ||
                course.program_type === programFilter;

            const matchesOwnership =
                !ownershipFilter ||
                (ownershipFilter === "DEPARTMENT"
                    ? course.is_department_owned
                    : !course.is_department_owned);

            return (
                matchesSearch &&
                matchesYear &&
                matchesSemester &&
                matchesProgram &&
                matchesOwnership
            );
        });
    }, [
        courses,
        search,
        yearFilter,
        semesterFilter,
        programFilter,
        ownershipFilter,
    ]);

    function handleInputChange(
        field: keyof CourseForm,
        value: string | boolean
    ) {
        setForm((previous) => ({
            ...previous,
            [field]: value,
        }));
    }

    function resetForm() {
        setForm(emptyForm);
        setEditingId(null);
    }

    function handleEdit(course: Course) {
        setForm({
            code: course.code,
            title: course.title,
            year_level: course.year_level.toString(),
            semester: course.semester.toString(),
            program_type: course.program_type,
            is_department_owned: course.is_department_owned,
        });

        setEditingId(course.id);
        setError("");
        setSuccess("");

        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setError("");
        setSuccess("");

        const payload = {
            code: form.code.trim().toUpperCase(),
            title: form.title.trim(),
            year_level: Number(form.year_level),
            semester: Number(form.semester),
            program_type: form.program_type,
            is_department_owned: form.is_department_owned,
        };

        if (!payload.code || !payload.title) {
            setError("Please enter both course code and course title.");
            return;
        }

        if (
            !Number.isInteger(payload.year_level) ||
            payload.year_level < 1
        ) {
            setError("Please select a valid year level.");
            return;
        }

        if (![1, 2].includes(payload.semester)) {
            setError("Please select a valid semester.");
            return;
        }

        setSaving(true);

        try {
            if (editingId !== null) {
                await API.patch(`courses/${editingId}/`, payload);
                setSuccess("Course updated successfully.");
            } else {
                await API.post("courses/", payload);
                setSuccess("Course added successfully.");
            }

            resetForm();
            loadCourses();
        } catch (err: any) {
            const data = err.response?.data;

            const message =
                data?.error ||
                data?.detail ||
                data?.code?.[0] ||
                data?.title?.[0];

            setError(
                message ||
                "Unable to save the course. Check the details and try again."
            );
        } finally {
            setSaving(false);
        }
    }

    return (
        <>
            <Header />

            <main className="dashboard">
                <section className="active-plan-card">
                    <h2>Courses</h2>

                    <p className="active-plan-description">
                        Manage regular and extension courses, including
                        department-owned and service courses.
                    </p>

                    <h3>
                        {editingId !== null ? "Edit Course" : "Add New Course"}
                    </h3>

                    <form className="form-container" onSubmit={handleSubmit}>
                        <label>
                            Course Code
                            <input
                                type="text"
                                value={form.code}
                                onChange={(e) =>
                                    handleInputChange("code", e.target.value)
                                }
                                placeholder="e.g. CoSc2022"
                                required
                            />
                        </label>

                        <label>
                            Course Title
                            <input
                                type="text"
                                value={form.title}
                                onChange={(e) =>
                                    handleInputChange("title", e.target.value)
                                }
                                placeholder="Enter course title"
                                required
                            />
                        </label>

                        <label>
                            Year Level
                            <select
                                value={form.year_level}
                                onChange={(e) =>
                                    handleInputChange("year_level", e.target.value)
                                }
                            >
                                {[1, 2, 3, 4].map((year) => (
                                    <option key={year} value={year}>
                                        Year {year}
                                    </option>
                                ))}
                            </select>
                        </label>

                        <label>
                            Semester
                            <select
                                value={form.semester}
                                onChange={(e) =>
                                    handleInputChange("semester", e.target.value)
                                }
                            >
                                <option value="1">Semester 1</option>
                                <option value="2">Semester 2</option>
                            </select>
                        </label>

                        <label>
                            Program Type
                            <select
                                value={form.program_type}
                                onChange={(e) =>
                                    handleInputChange(
                                        "program_type",
                                        e.target.value as ProgramType
                                    )
                                }
                            >
                                <option value="REGULAR">Regular</option>
                                <option value="EXTENSION">Extension</option>
                            </select>
                        </label>

                        <label>
                            Course Ownership
                            <select
                                value={
                                    form.is_department_owned ? "true" : "false"
                                }
                                onChange={(e) =>
                                    handleInputChange(
                                        "is_department_owned",
                                        e.target.value === "true"
                                    )
                                }
                            >
                                <option value="true">Department-owned</option>
                                <option value="false">Service course</option>
                            </select>
                        </label>

                        <button type="submit" disabled={saving}>
                            {saving
                                ? "Saving..."
                                : editingId !== null
                                    ? "Update Course"
                                    : "Add Course"}
                        </button>

                        {editingId !== null && (
                            <button
                                type="button"
                                onClick={resetForm}
                                disabled={saving}
                            >
                                Cancel Edit
                            </button>
                        )}
                    </form>

                    {error && (
                        <p className="error-message" role="alert">
                            {error}
                        </p>
                    )}

                    {success && (
                        <p role="status">
                            {success}
                        </p>
                    )}

                    <hr />

                    <h3>Registered Courses</h3>

                    <p>
                        Showing {filteredCourses.length} of {courses.length} courses.
                    </p>

                    <div className="course-filters">
                        <input
                            type="search"
                            placeholder="Search by course code or title"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />

                        <select
                            value={yearFilter}
                            onChange={(e) => setYearFilter(e.target.value)}
                        >
                            <option value="">All Year Levels</option>
                            {[1, 2, 3, 4].map((year) => (
                                <option key={year} value={year}>
                                    Year {year}
                                </option>
                            ))}
                        </select>

                        <select
                            value={semesterFilter}
                            onChange={(e) => setSemesterFilter(e.target.value)}
                        >
                            <option value="">All Semesters</option>
                            <option value="1">Semester 1</option>
                            <option value="2">Semester 2</option>
                        </select>

                        <select
                            value={programFilter}
                            onChange={(e) => setProgramFilter(e.target.value)}
                        >
                            <option value="">All Programs</option>
                            <option value="REGULAR">Regular</option>
                            <option value="EXTENSION">Extension</option>
                        </select>

                        <select
                            value={ownershipFilter}
                            onChange={(e) => setOwnershipFilter(e.target.value)}
                        >
                            <option value="">All Ownership Types</option>
                            <option value="DEPARTMENT">Department-owned</option>
                            <option value="SERVICE">Service courses</option>
                        </select>

                        <button
                            type="button"
                            onClick={() => {
                                setSearch("");
                                setYearFilter("");
                                setSemesterFilter("");
                                setProgramFilter("");
                                setOwnershipFilter("");
                            }}
                        >
                            Clear Filters
                        </button>
                    </div>

                    {loading ? (
                        <p>Loading courses...</p>
                    ) : (
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Course Code</th>
                                        <th>Course Title</th>
                                        <th>Year</th>
                                        <th>Semester</th>
                                        <th>Program</th>
                                        <th>Ownership</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {filteredCourses.length === 0 ? (
                                        <tr>
                                            <td colSpan={7}>
                                                No courses match your filters.
                                            </td>
                                        </tr>
                                    ) : (
                                        filteredCourses.map((course) => (
                                            <tr key={course.id}>
                                                <td>{course.code}</td>
                                                <td>{course.title}</td>
                                                <td>Year {course.year_level}</td>
                                                <td>Semester {course.semester}</td>
                                                <td>
                                                    {course.program_type === "REGULAR"
                                                        ? "Regular"
                                                        : "Extension"}
                                                </td>
                                                <td>
                                                    {course.is_department_owned
                                                        ? "Department-owned"
                                                        : "Service course"}
                                                </td>
                                                <td>
                                                    <button
                                                        type="button"
                                                        onClick={() => handleEdit(course)}
                                                    >
                                                        Edit
                                                    </button>
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </section>
            </main>
        </>
    );
}

export default Courses;
