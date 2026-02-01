from app.schemas.triage import TriageOut

def test_triage_schema():
    data = {"level": "GREEN", "red_flags": [], "specialty_needed": None, "safety": []}
    model = TriageOut.model_validate(data)
    assert model.level == 'GREEN'
