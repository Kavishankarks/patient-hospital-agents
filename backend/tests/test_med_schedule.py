from app.services.medication_tracker_service import MedicationTrackerService

def test_build_schedule():
    svc = MedicationTrackerService()
    plan = {"start_date": "2026-01-31", "medications": [{"name": "amoxicillin", "dose": "500mg", "times": ["08:00", "20:00"]}]}
    schedule = svc.build_schedule(plan, days=1)
    assert len(schedule) == 2
    assert schedule[0]['med_name'] == 'amoxicillin'
