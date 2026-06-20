from datetime import timedelta

from academics.models import Holiday, ExamSession
from rooms.models import Room
from staff.models import Staff

from allocations.models import ExamRoomAllocation
from .models import ExamSchedule, InvigilationAssignment


class SchedulingEngine:

    def __init__(self, plan, exams):
        self.plan = plan
        self.exams = exams

    # =====================================================
    # MAIN ENTRY
    # =====================================================
    def run(self):
        schedules = []

        current_date = self.plan.start_date
        session_index = 0

        sessions = self._load_sessions()

        for exam in self.exams:

            # Move to next valid exam day
            current_date = self._next_valid_day(current_date)

            # Select session based on policy
            session = self._select_session(sessions, session_index)

            schedule = ExamSchedule.objects.create(
                plan=self.plan,
                exam=exam,
                date=current_date,
                session=session,
                is_auto=True,
                is_final=False
            )

            # Allocate resources
            self._allocate_rooms(schedule)
            self._assign_invigilators(schedule)

            schedules.append(schedule)

            session_index += 1

            # Optional balancing: move date after full session cycle
            if self._should_increment_date(session_index, len(sessions)):
                current_date = self._next_valid_day(current_date)

        return schedules

    # =====================================================
    # SESSION LOGIC (STEP 5 CORE FIX)
    # =====================================================

    def _load_sessions(self):
        return list(ExamSession.objects.all().order_by("start_time"))

    def _select_session(self, sessions, index):

        if self.plan.session_policy == "MORNING":
            return next(s for s in sessions if s.name == "MORNING")

        if self.plan.session_policy == "AFTERNOON":
            return next(s for s in sessions if s.name == "AFTERNOON")

        # MIXED → balanced alternating
        return sessions[index % len(sessions)]

    def _should_increment_date(self, session_index, session_count):
        return session_index > 0 and session_index % session_count == 0

    # =====================================================
    # DATE LOGIC
    # =====================================================

    def _is_valid_day(self, date):

        if date.weekday() >= 5:
            return False

        if Holiday.objects.filter(date=date).exists():
            return False

        return True

    def _next_valid_day(self, date):

        candidate = date + timedelta(days=1)

        while not self._is_valid_day(candidate):
            candidate += timedelta(days=1)

        return candidate

    # =====================================================
    # ROOM ALLOCATION
    # =====================================================

    def _allocate_rooms(self, schedule):

        students = schedule.exam.total_students

        occupied = ExamRoomAllocation.objects.filter(
            exam_schedule__date=schedule.date,
            exam_schedule__session=schedule.session
        ).values_list("room_id", flat=True)

        available_rooms = Room.objects.filter(
            is_active=True
        ).exclude(id__in=occupied)

        classrooms = available_rooms.filter(
            room_type=Room.CLASSROOM
        ).order_by("-exam_capacity")

        halls = available_rooms.filter(
            room_type=Room.HALL
        ).order_by("-exam_capacity")

        # classrooms first
        for room in classrooms:
            if students <= 0:
                break

            assigned = min(room.exam_capacity, students)

            ExamRoomAllocation.objects.create(
                exam_schedule=schedule,
                room=room,
                allocated_students=assigned
            )

            students -= assigned

        # halls if needed
        if students > 0:
            for hall in halls:
                if students <= 0:
                    break

                assigned = min(hall.exam_capacity, students)

                ExamRoomAllocation.objects.create(
                    exam_schedule=schedule,
                    room=hall,
                    allocated_students=assigned
                )

                students -= assigned

    # =====================================================
    # INVIGILATION
    # =====================================================

    def _required_invigilators(self, schedule):

        total = 0

        allocations = ExamRoomAllocation.objects.filter(
            exam_schedule=schedule
        )

        for a in allocations:
            if a.room.room_type == Room.HALL:
                total += 2
            else:
                total += 1

        return total

    def _busy_staff(self, date, session):

        return Staff.objects.filter(
            invigilationassignment__exam_schedule__date=date,
            invigilationassignment__exam_schedule__session=session
        ).distinct()

    def _available_staff(self, schedule, max_per_day=2):

        return Staff.objects.filter(is_active=True).exclude(
            id__in=Staff.objects.filter(
                invigilationassignment__exam_schedule__date=schedule.date
            ).values_list("id", flat=True)
        )

    def _assign_invigilators(self, schedule):

        required = self._required_invigilators(schedule)

        staff_qs = self._available_staff(schedule).exclude(
            id__in=self._busy_staff(schedule.date, schedule.session)
        ).order_by("id")

        for staff in staff_qs[:required]:

            InvigilationAssignment.objects.create(
                exam_schedule=schedule,
                staff=staff,
                is_auto=True
            )

    def regenerate(self):

        # Only delete SYSTEM-GENERATED schedules
        ExamSchedule.objects.filter(
            plan=self.plan,
            is_auto=True,
            is_locked=False
        ).delete()

        # Re-run engine
        return self.run()