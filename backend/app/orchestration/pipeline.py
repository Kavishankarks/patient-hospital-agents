from __future__ import annotations
from app.agents.profiler_agent import ProfilerAgent
from app.agents.medrecon_agent import MedReconAgent
from app.agents.triage_gate_agent import TriageGateAgent
from app.agents.summary_agent import SummaryAgent
from app.agents.preintelligence_agent import PreIntelligenceAgent
from app.agents.recovery_coach_agent import RecoveryCoachAgent
from app.services.interaction_rules_service import InteractionRulesService
from app.services.hospital_mcp_service import HospitalMCPService
from app.services.medication_tracker_service import MedicationTrackerService
from app.services.tts_service import TTSService

async def build_patient_profile(input_text: str) -> tuple[dict, dict]:
    profile = ProfilerAgent().run(input_text)
    meds = MedReconAgent().run(input_text)
    triage = TriageGateAgent().run(input_text)
    return profile.model_dump(), {
        'medications': meds.model_dump().get('medications', []),
        'triage': triage.model_dump(),
    }

async def generate_doctor_bundle(input_text: str, meds_list: list[str], triage_level: str, specialty_needed: str | None, location: str, radius_km: int) -> dict:
    sbar = SummaryAgent().run(input_text)
    pre = PreIntelligenceAgent().run(input_text)
    interactions = InteractionRulesService().check(meds_list)
    pre.interactions.extend(interactions)
    hospitals = []
    if triage_level in {'RED', 'AMBER'}:
        mcp = HospitalMCPService()
        found = await mcp.search(location, radius_km, specialty_needed, triage_level)
        hospitals = mcp.rank_hospitals(found, specialty_needed, triage_level)
    return {
        'sbar': sbar.model_dump(),
        'preintelligence': pre.model_dump(),
        'hospitals': hospitals,
    }

async def activate_med_plan(plan_json: dict) -> list[dict]:
    tracker = MedicationTrackerService()
    return tracker.build_schedule(plan_json, days=1)

async def generate_daily_coach(input_text: str) -> tuple[str, str]:
    script = RecoveryCoachAgent().run(input_text)
    audio_path = TTSService().synthesize(script)
    return script, audio_path
