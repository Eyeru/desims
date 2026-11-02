
import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import API from "../services/api";
import Header from "../components/Header";

type RoomType = "CLASSROOM" | "HALL";

interface Room {
    id: number;
    name: string;
    building: string;
    physical_capacity: number;
    exam_capacity: number;
    room_type: RoomType;
    is_active: boolean;
    department: string | null;
}

interface RoomForm {
    name: string;
    building: string;
    physical_capacity: string;
    exam_capacity: string;
    room_type: RoomType;
    is_active: boolean;
    department: string;
}

const initialForm: RoomForm = {
    name: "",
    building: "",
    physical_capacity: "",
    exam_capacity: "",
    room_type: "CLASSROOM",
    is_active: true,
    department: "Computer Science",
};

function Rooms() {
    const [rooms, setRooms] = useState<Room[]>([]);
    const [form, setForm] = useState<RoomForm>(initialForm);
    const [editingId, setEditingId] = useState<number | null>(null);

    const [search, setSearch] = useState("");
    const [buildingFilter, setBuildingFilter] = useState("");
    const [typeFilter, setTypeFilter] = useState("");
    const [statusFilter, setStatusFilter] = useState("");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const loadRooms = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await API.get<Room[]>("rooms/");
            setRooms(response.data);
        } catch {
            setError("Unable to load rooms. Please check the server.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadRooms();
    }, []);

    const buildings = useMemo(
        () => [...new Set(rooms.map((room) => room.building))].sort(),
        [rooms]
    );

    const filteredRooms = useMemo(() => {
        return rooms.filter((room) => {
            const searchMatch =
                room.name.toLowerCase().includes(search.toLowerCase()) ||
                room.building.toLowerCase().includes(search.toLowerCase()) ||
                (room.department || "").toLowerCase().includes(search.toLowerCase());

            const buildingMatch =
                !buildingFilter || room.building === buildingFilter;

            const typeMatch =
                !typeFilter || room.room_type === typeFilter;

            const statusMatch =
                !statusFilter ||
                (statusFilter === "ACTIVE" && room.is_active) ||
                (statusFilter === "INACTIVE" && !room.is_active);

            return searchMatch && buildingMatch && typeMatch && statusMatch;
        });
    }, [rooms, search, buildingFilter, typeFilter, statusFilter]);

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        setError("");
        setSuccess("");

        const physicalCapacity = Number(form.physical_capacity);
        const examCapacity = Number(form.exam_capacity);

        if (!form.name.trim() || !form.building.trim()) {
            setError("Room name and building are required.");
            return;
        }

        if (
            !Number.isInteger(physicalCapacity) ||
            !Number.isInteger(examCapacity) ||
            physicalCapacity < 1 ||
            examCapacity < 1
        ) {
            setError("Capacities must be positive whole numbers.");
            return;
        }

        if (examCapacity > physicalCapacity) {
            setError("Exam capacity cannot exceed physical capacity.");
            return;
        }

        const payload = {
            name: form.name.trim(),
            building: form.building.trim(),
            physical_capacity: physicalCapacity,
            exam_capacity: examCapacity,
            room_type: form.room_type,
            is_active: form.is_active,
            department: form.department.trim() || null,
        };

        try {
            setSaving(true);

            if (editingId !== null) {
                await API.patch(`rooms/${editingId}/`, payload);
                setSuccess("Room updated successfully.");
            } else {
                await API.post("rooms/", payload);
                setSuccess("Room added successfully.");
            }

            setForm(initialForm);
            setEditingId(null);
            await loadRooms();
        } catch (err: any) {
            setError(
                err.response?.data?.error ||
                "Unable to save room. Please check your information."
            );
        } finally {
            setSaving(false);
        }
    };

    const handleEdit = (room: Room) => {
        setEditingId(room.id);
        setForm({
            name: room.name,
            building: room.building,
            physical_capacity: String(room.physical_capacity),
            exam_capacity: String(room.exam_capacity),
            room_type: room.room_type,
            is_active: room.is_active,
            department: room.department || "",
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

    const toggleRoomStatus = async (room: Room) => {
        const action = room.is_active ? "deactivate" : "activate";

        if (!window.confirm(`Are you sure you want to ${action} ${room.name}?`)) {
            return;
        }

        setError("");
        setSuccess("");

        try {
            await API.patch(`rooms/${room.id}/`, {
                is_active: !room.is_active,
            });

            setSuccess(`${room.name} ${action}d successfully.`);
            await loadRooms();
        } catch (err: any) {
            setError(
                err.response?.data?.error ||
                `Unable to ${action} room.`
            );
        }
    };

    return (
        <div className="dashboard">
            <Header />

            <main className="page-container">
                <h1>Room Management</h1>
                <p>
                    Manage examination rooms, capacities, buildings,
                    and room availability.
                </p>

                <form className="form-container" onSubmit={handleSubmit}>
                    <h2>
                        {editingId !== null ? "Edit Room" : "Add New Room"}
                    </h2>

                    {error && <div className="error-message">{error}</div>}
                    {success && <div className="success-message">{success}</div>}

                    <label>
                        Room Name
                        <input
                            type="text"
                            value={form.name}
                            onChange={(e) =>
                                setForm({ ...form, name: e.target.value })
                            }
                            placeholder="e.g. E1"
                            required
                        />
                    </label>

                    <label>
                        Building
                        <input
                            type="text"
                            value={form.building}
                            onChange={(e) =>
                                setForm({ ...form, building: e.target.value })
                            }
                            placeholder="e.g. T14"
                            required
                        />
                    </label>

                    <label>
                        Physical Capacity
                        <input
                            type="number"
                            min="1"
                            step="1"
                            value={form.physical_capacity}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    physical_capacity: e.target.value,
                                })
                            }
                            required
                        />
                    </label>

                    <label>
                        Exam Capacity
                        <input
                            type="number"
                            min="1"
                            step="1"
                            value={form.exam_capacity}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    exam_capacity: e.target.value,
                                })
                            }
                            required
                        />
                    </label>

                    <label>
                        Room Type
                        <select
                            value={form.room_type}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    room_type: e.target.value as RoomType,
                                })
                            }
                        >
                            <option value="CLASSROOM">Classroom</option>
                            <option value="HALL">Hall</option>
                        </select>
                    </label>

                    <label>
                        Department
                        <input
                            type="text"
                            value={form.department}
                            onChange={(e) =>
                                setForm({ ...form, department: e.target.value })
                            }
                            placeholder="e.g. Computer Science"
                        />
                    </label>

                    <label>
                        Room Status
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
                                    ? "Update Room"
                                    : "Add Room"}
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
                    <h2>Rooms List</h2>

                    <div className="course-filters">
                        <input
                            type="text"
                            placeholder="Search room, building, department..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />

                        <select
                            value={buildingFilter}
                            onChange={(e) => setBuildingFilter(e.target.value)}
                        >
                            <option value="">All Buildings</option>
                            {buildings.map((building) => (
                                <option key={building} value={building}>
                                    {building}
                                </option>
                            ))}
                        </select>

                        <select
                            value={typeFilter}
                            onChange={(e) => setTypeFilter(e.target.value)}
                        >
                            <option value="">All Room Types</option>
                            <option value="CLASSROOM">Classroom</option>
                            <option value="HALL">Hall</option>
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
                            <p>Loading rooms...</p>
                        ) : (
                            <table>
                                <thead>
                                    <tr>
                                        <th>Room</th>
                                        <th>Building</th>
                                        <th>Physical Capacity</th>
                                        <th>Exam Capacity</th>
                                        <th>Type</th>
                                        <th>Department</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {filteredRooms.length === 0 ? (
                                        <tr>
                                            <td colSpan={8}>
                                                No rooms found.
                                            </td>
                                        </tr>
                                    ) : (
                                        filteredRooms.map((room) => (
                                            <tr key={room.id}>
                                                <td>{room.name}</td>
                                                <td>{room.building}</td>
                                                <td>{room.physical_capacity}</td>
                                                <td>{room.exam_capacity}</td>
                                                <td>
                                                    {room.room_type === "HALL"
                                                        ? "Hall"
                                                        : "Classroom"}
                                                </td>
                                                <td>{room.department || "—"}</td>
                                                <td>
                                                    {room.is_active
                                                        ? "Active"
                                                        : "Inactive"}
                                                </td>
                                                <td>
                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            handleEdit(room)
                                                        }
                                                    >
                                                        Edit
                                                    </button>{" "}
                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            toggleRoomStatus(room)
                                                        }
                                                    >
                                                        {room.is_active
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
                            Showing {filteredRooms.length} of {rooms.length} rooms.
                        </p>
                    )}
                </section>
            </main>
        </div>
    );
}

export default Rooms;
