from __future__ import annotations
from datetime import datetime, timedelta

class MedicationTrackerService:
    def build_schedule(self, plan_json: dict, days: int = 1) -> list[dict]:
        schedule = []
        start_date = plan_json.get('start_date')
        meds = plan_json.get('medications', [])
        now = datetime.utcnow()
        for day in range(days):
            base = now + timedelta(days=day)
            for med in meds:
                times = med.get('times') or ['08:00']
                for t in times:
                    due_at = f"{base.date().isoformat()}T{t}:00Z"
                    schedule.append({
                        'med_name': med.get('name'),
                        'dose': med.get('dose'),
                        'due_at': due_at,
                        'status': 'pending',
                    })
        return schedule
