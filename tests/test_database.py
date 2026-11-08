"""
AttendSync Database Layer & CLI Tests
-------------------------------------
Validates SQLAlchemy models, composite constraints, cascade delete,
CRUD helper utilities, and Flask CLI commands.
"""

from datetime import date, timedelta
import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import AttendanceRecord, AttendanceStatus, Student
from app.crud import (
    create_student,
    get_all_students_sorted,
    get_attendance_by_date,
    get_student_attendance_history,
    get_student_attendance_summary,
    get_student_by_usn,
    record_attendance,
)


def test_student_creation(app):
    """Test standard Student creation and attributes."""
    with app.app_context():
        student = create_student(
            usn="1MS21CS101",
            name="Rahul Dev",
            email="rahul.dev@college.edu",
            department="Computer Science & Engineering",
            semester=6,
            section="A"
        )
        assert student.id is not None
        assert student.usn == "1MS21CS101"
        assert repr(student).startswith("<Student")


def test_student_usn_uniqueness(app):
    """Ensure duplicate USN raises IntegrityError."""
    with app.app_context():
        create_student("1MS21CS102", "Student One", "s1@college.edu", "CSE", 6, "A")
        with pytest.raises(IntegrityError):
            create_student("1MS21CS102", "Student Two", "s2@college.edu", "CSE", 6, "A")
        db.session.rollback()


def test_student_email_uniqueness(app):
    """Ensure duplicate Email raises IntegrityError."""
    with app.app_context():
        create_student("1MS21CS103", "Student Three", "shared@college.edu", "CSE", 6, "A")
        with pytest.raises(IntegrityError):
            create_student("1MS21CS104", "Student Four", "shared@college.edu", "CSE", 6, "A")
        db.session.rollback()


def test_composite_unique_constraint_student_date(app):
    """
    Verify database-level composite unique constraint (student_id, date).
    A student cannot have two attendance records on the exact same date.
    """
    with app.app_context():
        student = create_student("1MS21CS105", "Test Student", "t105@college.edu", "CSE", 6, "A")
        today = date.today()

        rec1 = AttendanceRecord(student_id=student.id, date=today, status="Present")
        db.session.add(rec1)
        db.session.commit()

        # Attempt to insert a second attendance record for the same student and same day
        rec2 = AttendanceRecord(student_id=student.id, date=today, status="Absent")
        db.session.add(rec2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_cascade_delete_attendance_records(app):
    """
    Verify cascade delete: Deleting a Student must automatically delete
    all associated AttendanceRecord rows.
    """
    with app.app_context():
        student = create_student("1MS21CS106", "Cascade Test", "casc@college.edu", "ECE", 4, "B")
        today = date.today()
        yesterday = today - timedelta(days=1)

        db.session.add_all([
            AttendanceRecord(student_id=student.id, date=yesterday, status="Present"),
            AttendanceRecord(student_id=student.id, date=today, status="Absent"),
        ])
        db.session.commit()

        student_id = student.id
        # Confirm 2 records exist
        records = AttendanceRecord.query.filter_by(student_id=student_id).all()
        assert len(records) == 2

        # Delete student
        db.session.delete(student)
        db.session.commit()

        # Verify attendance records were deleted by cascade
        orphaned = AttendanceRecord.query.filter_by(student_id=student_id).all()
        assert len(orphaned) == 0


def test_crud_get_all_students_sorted(app):
    """Verify get_all_students_sorted() returns students sorted alphabetically by USN."""
    with app.app_context():
        create_student("1MS21CS030", "Charlie", "c@college.edu", "CSE", 6, "A")
        create_student("1MS21CS010", "Alice", "a@college.edu", "CSE", 6, "A")
        create_student("1MS21CS020", "Bob", "b@college.edu", "CSE", 6, "A")

        students = get_all_students_sorted()
        usns = [s.usn for s in students]
        assert usns == ["1MS21CS010", "1MS21CS020", "1MS21CS030"]


def test_crud_get_attendance_by_date(app):
    """Verify get_attendance_by_date() retrieves records for a given date."""
    with app.app_context():
        s1 = create_student("1MS21CS001", "Student 1", "s1@test.com", "CSE", 6, "A")
        s2 = create_student("1MS21CS002", "Student 2", "s2@test.com", "CSE", 6, "A")
        target_day = date(2026, 11, 8)
        other_day = date(2026, 11, 7)

        db.session.add_all([
            AttendanceRecord(student_id=s1.id, date=target_day, status="Present"),
            AttendanceRecord(student_id=s2.id, date=target_day, status="Absent"),
            AttendanceRecord(student_id=s1.id, date=other_day, status="Present"),
        ])
        db.session.commit()

        # Query using date object
        records = get_attendance_by_date(target_day)
        assert len(records) == 2
        assert records[0].student.usn == "1MS21CS001"
        assert records[0].status == "Present"
        assert records[1].student.usn == "1MS21CS002"
        assert records[1].status == "Absent"

        # Query using ISO string
        records_str = get_attendance_by_date("2026-11-08")
        assert len(records_str) == 2


def test_crud_get_student_attendance_history(app):
    """Verify get_student_attendance_history() retrieves chronological records for a student."""
    with app.app_context():
        student = create_student("1MS21CS050", "History Test", "hist@college.edu", "ISE", 4, "B")
        d1 = date(2026, 11, 1)
        d2 = date(2026, 11, 2)
        d3 = date(2026, 11, 3)

        db.session.add_all([
            AttendanceRecord(student_id=student.id, date=d1, status="Present"),
            AttendanceRecord(student_id=student.id, date=d2, status="Absent"),
            AttendanceRecord(student_id=student.id, date=d3, status="Present"),
        ])
        db.session.commit()

        st, history = get_student_attendance_history("1MS21CS050")
        assert st is not None
        assert st.usn == "1MS21CS050"
        assert len(history) == 3
        # Should be sorted newest first
        assert history[0].date == d3
        assert history[1].date == d2
        assert history[2].date == d1

        # Summary helper check
        summary = get_student_attendance_summary("1MS21CS050")
        assert summary["total_classes"] == 3
        assert summary["present_count"] == 2
        assert summary["absent_count"] == 1
        assert summary["attendance_percentage"] == 66.67


def test_crud_record_attendance_upsert(app):
    """Verify record_attendance() handles both initial creation and update without duplicate errors."""
    with app.app_context():
        create_student("1MS21CS099", "Upsert Student", "up@test.com", "CSE", 6, "A")
        record_date = date(2026, 11, 8)

        # First insert
        rec1 = record_attendance("1MS21CS099", record_date, "Present")
        assert rec1.status == "Present"

        # Update on the same day
        rec2 = record_attendance("1MS21CS099", record_date, "Absent")
        assert rec2.id == rec1.id
        assert rec2.status == "Absent"

        # Check only 1 record exists
        count = AttendanceRecord.query.filter_by(date=record_date).count()
        assert count == 1


def test_cli_init_db(runner):
    """Verify 'flask init-db' CLI command executes cleanly."""
    result = runner.invoke(args=["init-db"])
    assert result.exit_code == 0
    assert "Database initialized successfully" in result.output


def test_cli_seed_db(runner):
    """Verify 'flask seed-db' CLI command seeds sample students and attendance."""
    result = runner.invoke(args=["seed-db"])
    assert result.exit_code == 0
    assert "AttendSync Database Seeding Completed!" in result.output
    assert "Students" in result.output
    assert "Attendance" in result.output
