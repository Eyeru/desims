from scheduling.services import generate_schedule
from allocations.services import allocate_rooms
from invigilation.services import assign_invigilators
from conflicts.services import run_all_conflicts


def generate_full_exam_plan(exams, exam_period, default_session):
    """
    Main system engine (single entry point)
    """

    results = {
        "schedule": [],
        "allocations": [],
        "invigilations": [],
        "conflicts": []
    }

    # STEP 1: Schedule exams
    schedule = generate_schedule(exams, exam_period, default_session)
    results["schedule"] = schedule

    # STEP 2 + 3 per exam
    for s in schedule:
        exam = s.exam

        # allocate rooms
        success, allocations = allocate_rooms(exam)

        if not success:
            results["conflicts"].append(allocations)
            continue

        results["allocations"].extend(allocations)

        # assign invigilators
        rooms = [a.room for a in allocations]
        invig = assign_invigilators(exam, rooms)

        results["invigilations"].extend(invig)

        # STEP 4: conflict detection
        conflicts = run_all_conflicts(s, [], rooms)
        results["conflicts"].extend(conflicts)

    return results