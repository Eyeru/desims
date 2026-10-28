
import { useEffect, useState } from "react";
import API from "../services/api";
import type { AcademicYear } from "../types/AcademicYear";

function AcademicYears() {
    const [years, setYears] = useState<AcademicYear[]>([]);
    const [yearName, setYearName] = useState("");
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    function loadYears() {
        setLoading(true);

        API.get<AcademicYear[]>("academic-years/")
            .then((response) => {
                setYears(response.data);
                setError("");
            })
            .catch(() => {
                setError("Failed to load academic years.");
            })
            .finally(() => {
                setLoading(false);
            });
    }

    useEffect(() => {
        loadYears();
    }, []);

    async function handleSubmit(
        event: React.FormEvent<HTMLFormElement>
    ) {
        event.preventDefault();
        setError("");
        setSuccess("");

        const name = yearName.trim();

        if (!name) {
            setError("Please enter an academic year.");
            return;
        }

        setSaving(true);

        try {
            await API.post("academic-years/", { name });

            setYearName("");
            setSuccess("Academic year created successfully.");
            loadYears();
        } catch (err: any) {
            const message = err.response?.data?.error;
            setError(message || "Failed to create academic year.");
        } finally {
            setSaving(false);
        }
    }

    return (
        <main className="dashboard">
            <section className="active-plan-card">
                <h2>Academic Years</h2>

                <p className="active-plan-description">
                    Manage the academic years registered in DESIMS.
                </p>

                <form onSubmit={handleSubmit}>
                    <label htmlFor="academic-year-name">
                        Academic year
                    </label>

                    <div>
                        <input
                            id="academic-year-name"
                            type="text"
                            placeholder="e.g. 2026/2027"
                            value={yearName}
                            onChange={(event) =>
                                setYearName(event.target.value)
                            }
                            disabled={saving}
                        />

                        <button type="submit" disabled={saving}>
                            {saving ? "Saving..." : "Add Academic Year"}
                        </button>
                    </div>
                </form>

                {error && <p role="alert">{error}</p>}
                {success && <p role="status">{success}</p>}

                <h3>Registered Academic Years</h3>

                {loading && <p>Loading academic years...</p>}

                {!loading && !error && years.length === 0 && (
                    <p>No academic years have been registered yet.</p>
                )}

                {!loading && years.length > 0 && (
                    <table>
                        <thead>
                            <tr>
                                <th>Academic Year</th>
                                <th>Status</th>
                            </tr>
                        </thead>

                        <tbody>
                            {years.map((year) => (
                                <tr key={year.id}>
                                    <td>{year.name}</td>
                                    <td>
                                        {year.is_active ? "Active" : "Inactive"}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </section>
        </main>
    );
}

export default AcademicYears;
