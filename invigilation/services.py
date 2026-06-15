from .models import InvigilationAssignment, StaffWorkload
from staff.models import Staff


def get_least_loaded_staff(exclude_ids):
    staff_list = Staff.objects.filter(is_active=True).exclude(id__in=exclude_ids)

    workloads = StaffWorkload.objects.filter(staff__in=staff_list)

    workload_map = {w.staff_id: w.total_assignments for w in workloads}

    # default 0 if not found
    def get_load(s):
        return workload_map.get(s.id, 0)

    sorted_staff = sorted(staff_list, key=get_load)

    return sorted_staff


def assign_invigilators(exam, rooms, required_per_room=1):
    assignments = []

    for room in rooms:
        assigned_staff_ids = []

        for _ in range(required_per_room):

            staff_list = get_least_loaded_staff(assigned_staff_ids)

            if not staff_list:
                continue

            staff = staff_list[0]

            assignment = InvigilationAssignment.objects.create(
                exam=exam,
                room=room,
                staff=staff,
                is_auto=True
            )

            assignments.append(assignment)

            assigned_staff_ids.append(staff.id)

            # update workload
            wl, _ = StaffWorkload.objects.get_or_create(staff=staff)
            wl.total_assignments += 1
            wl.save()

    return assignments