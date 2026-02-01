from app.services.hospital_mcp_service import HospitalMCPService

def test_rank_hospitals():
    svc = HospitalMCPService()
    hospitals = [
        {"id": "A", "name": "Alpha", "specialties": ["cardiology"], "trauma_level": 1, "eta_min": 10},
        {"id": "B", "name": "Beta", "specialties": [], "trauma_level": 0, "eta_min": 5},
    ]
    ranked = svc.rank_hospitals(hospitals, "cardiology", "RED")
    assert ranked[0]['hospital_id'] == 'A'
