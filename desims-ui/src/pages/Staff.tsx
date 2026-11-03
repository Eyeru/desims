
import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import API from "../services/api";
import Header from "../components/Header";

type StaffType = "INSTRUCTOR" | "TECH_ASSISTANT";
type ProgramType = "REGULAR" | "EXTENSION" | "BOTH";

interface StaffMember {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    staff_type: StaffType;
    program_type: ProgramType;
    department: string;
    is_active: boolean;
}

interface StaffForm {
    first_name: string;
    last_name: string;
    email: string;
    staff_type: StaffType;
    program_type: ProgramType;
    department: string;
    is_active: boolean;
}

const initialForm: StaffForm = {
    first_name: "",
    last_name: "",
    email: "",
    staff_type: "INSTRUCTOR",
    program_type: "BOTH",
    department: "Computer Science",
    is_active: true,
};

function Staff() {
    const [staffMembers, setStaffMembers] = useState<StaffMember[]>([]);
    const [form, setForm] = useState<StaffForm>(initialForm);
    const [editingId, setEditingId] = useState<number | null>(null);

    const [search, setSearch] = useState("");
    const [typeFilter, setTypeFilter] = useState("");
    const [programFilter, setProgramFilter] = useState("");
    const [statusFilter, setStatusFilter] = useState("");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const loadStaff = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await API.get<StaffMember[]>("staff/");
            setStaffMembers(response.data);
        } catch {
            setError("Unable to load staff. Please check the server.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadStaff();
    }, []);

    const filteredStaff = useMemo(() => {
        return staffMembers.filter((member) => {
            const fullName =
                `${member.first_name} ${member.last_name}`.toLowerCase();

            const searchMatch =
                fullName.includes(search.toLowerCase()) ||
                member.email.toLowerCase().includes(search.toLowerCase()) ||
                member.department.toLowerCase().includes(search.toLowerCase());

            const typeMatch =
                !typeFilter || member.staff_type === typeFilter;

            const programMatch =
                !programFilter || member.program_type === programFilter;

            const statusMatch =
                !statusFilter ||
                (statusFilter === "ACTIVE" && member.is_active) ||
                (statusFilter === "INACTIVE" && !member.is_active);

            return searchMatch && typeMatch && programMatch && statusMatch;
        });
    }, [staffMembers, search, typeFilter, programFilter, statusFilter]);

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        setError("");
        setSuccess("");

        const payload = {
            ...form,
            first_name: form.first_name.trim(),
            last_name: form.last_name.trim(),
            email: form.email.trim(),
            department: form.department.trim() || "Computer Science",
        };

        try {
            setSaving(true);

            if (editingId !== null) {
                await API.patch(`staff/${editingId}/`, payload);
                setSuccess("Staff member updated successfully.");
            } else {
                await API.post("staff/", payload);
                setSuccess("Staff member added successfully.");
            }

            setForm(initialForm);
            setEditingId(null);
            await loadStaff();
        } catch (err: any) {
            const data = err.response?.data;

            if (data?.email) {
                setError(
                    Array.isArray(data.email)
                        ? data.email.join(" ")
                        : data.email
                );
            } else if (data && typeof data === "object") {
                setError(
                    Object.entries(data)
                        .map(([field, messages]) =>
                            `${field}: ${
                                Array.isArray(messages)
                                    ? messages.join(" ")
                                    : String(messages)
                            }`
                        )
                        .join(" | ")
                );
            } else {
                setError("Unable to save staff member. Please try again.");
            }
        } finally {
            setSaving(false);
        }
    };

    const handleEdit = (member: StaffMember) => {
        setEditingId(member.id);
        setForm({
            first_name: member.first_name,
            last_name: member.last_name,
            email: member.email,
            staff_type: member.staff_type,
            program_type: member.program_type,
            department: member.department,
            is_active: member.is_active,
        });

        setError("");
        setSuccess("");
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    const cancelEdit = () => {
        setEditingId(null);
        setForm(initialForm);
        setError("");
        setSuccess("");
    };

    const toggleStaffStatus = async (member: StaffMember) => {
        const action = member.is_active ? "deactivate" : "activate";

        if (
            !window.confirm(
                `Are you sure you want to ${action} ${member.first_name} ${member.last_name}?`
            )
        ) {
            return;
        }

        setError("");
        setSuccess("");

        try {
            await API.patch(`staff/${member.id}/`, {
                is_active: !member.is_active,
            });

            setSuccess(
                `${member.first_name} ${action}d successfully.`
            );
            await loadStaff();
        } catch (err: any) {
            setError(
                err.response?.data?.error ||
                `Unable to ${action} staff member.`
            );
        }
    };

    return (
        <div className="dashboard">
            <Header />

            <main className="page-container">
                <h1>Staff Management</h1>
                <p>
                    Manage department instructors and technical assistants.
                </p>

                <form className="form-container" onSubmit={handleSubmit}>
                    <h2>
                        {editingId !== null
                            ? "Edit Staff Member"
                            : "Add New Staff Member"}
                    </h2>

                    {error && (
                        <div className="error-message">{error}</div>
                    )}

                    {success && (
                        <div className="success-message">{success}</div>
                    )}

                    <label>
                        First Name
                        <input
                            type="text"
                            value={form.first_name}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    first_name: e.target.value,
                                })
                            }
                            required
                        />
                    </label>

                    <label>
                        Last Name
                        <input
                            type="text"
                            value={form.last_name}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    last_name: e.target.value,
                                })
                            }
                            required
                        />
                    </label>

                    <label>
                        Email
                        <input
                            type="email"
                            value={form.email}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    email: e.target.value,
                                })
                            }
                            required
                        />
                    </label>

                    <label>
                        Staff Type
                        <select
                            value={form.staff_type}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    staff_type: e.target.value as StaffType,
                                })
                            }
                        >
                            <option value="INSTRUCTOR">Instructor</option>
                            <option value="TECH_ASSISTANT">
                                Technical Assistant
                            </option>
                        </select>
                    </label>

                    <label>
                        Program Type
                        <select
                            value={form.program_type}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    program_type: e.target.value as ProgramType,
                                })
                            }
                        >
                            <option value="REGULAR">Regular</option>
                            <option value="EXTENSION">Extension</option>
                            <option value="BOTH">Both</option>
                        </select>
                    </label>

                    <label>
                        Department
                        <input
                            type="text"
                            value={form.department}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    department: e.target.value,
                                })
                            }
                        />
                    </label>

                    <label>
                        Staff Status
                        <select
                            value={form.is_active ? "true" : "false"}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    is_active: e.target.value === "true",
                                })
                            }
                        >
                            <option value="true">Active</option>
                            <option value="false">Inactive</option>
                        </select>
                    </label>

                    <div className="room-form-actions">
                        <button type="submit" disabled={saving}>
                            {saving
                                ? "Saving..."
                                : editingId !== null
                                    ? "Update Staff"
                                    : "Add Staff"}
                        </button>

                        {editingId !== null && (
                            <button
                                type="button"
                                className="room-cancel-button"
                                onClick={cancelEdit}
                            >
                                Cancel
                            </button>
                        )}
                    </div>
                </form>

                <section>
                    <h2>Staff List</h2>

                    <div className="course-filters">
                        <input
                            type="text"
                            placeholder="Search name, email, department..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />

                        <select
                            value={typeFilter}
                            onChange={(e) => setTypeFilter(e.target.value)}
                        >
                            <option value="">All Staff Types</option>
                            <option value="INSTRUCTOR">Instructors</option>
                            <option value="TECH_ASSISTANT">
                                Technical Assistants
                            </option>
                        </select>

                        <select
                            value={programFilter}
                            onChange={(e) => setProgramFilter(e.target.value)}
                        >
                            <option value="">All Programs</option>
                            <option value="REGULAR">Regular</option>
                            <option value="EXTENSION">Extension</option>
                            <option value="BOTH">Both</option>
                        </select>

                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                        >
                            <option value="">All Statuses</option>
                            <option value="ACTIVE">Active</option>
                            <option value="INACTIVE">Inactive</option>
                        </select>
                    </div>

                    <div className="table-container">
                        {loading ? (
                            <p>Loading staff...</p>
                        ) : (
                            <table>
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Staff Type</th>
                                        <th>Program</th>
                                        <th>Department</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {filteredStaff.length === 0 ? (
                                        <tr>
                                            <td colSpan={7}>
                                                No staff members found.
                                            </td>
                                        </tr>
                                    ) : (
                                        filteredStaff.map((member) => (
                                            <tr key={member.id}>
                                                <td>
                                                    {member.first_name}{" "}
                                                    {member.last_name}
                                                </td>
                                                <td>{member.email}</td>
                                                <td>
                                                    {member.staff_type ===
                                                    "TECH_ASSISTANT"
                                                        ? "Technical Assistant"
                                                        : "Instructor"}
                                                </td>
                                                <td>
                                                    {member.program_type === "BOTH"
                                                        ? "Both"
                                                        : member.program_type ===
                                                          "REGULAR"
                                                            ? "Regular"
                                                            : "Extension"}
                                                </td>
                                                <td>{member.department}</td>
                                                <td>
                                                    {member.is_active
                                                        ? "Active"
                                                        : "Inactive"}
                                                </td>
                                                <td>
                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            handleEdit(member)
                                                        }
                                                    >
                                                        Edit
                                                    </button>{" "}
                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            toggleStaffStatus(member)
                                                        }
                                                    >
                                                        {member.is_active
                                                            ? "Deactivate"
                                                            : "Activate"}
                                                    </button>
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        )}
                    </div>

                    {!loading && (
                        <p>
                            Showing {filteredStaff.length} of{" "}
                            {staffMembers.length} staff members.
                        </p>
                    )}
                </section>
            </main>
        </div>
    );
}

export default Staff;
