from fastapi import APIRouter, Query
from app.services.hospital_mcp_service import HospitalMCPService
from app.schemas.hospital import HospitalOut

router = APIRouter()

@router.get('/{patient_id}/hospitals/recommendations', response_model=list[HospitalOut])
async def hospital_recommendations(patient_id: int, radius_km: int = Query(default=20)):
    """Recommend hospitals based on triage urgency and specialty match."""
    mcp = HospitalMCPService()
    hospitals = await mcp.search('unknown', radius_km, None, 'AMBER')
    return mcp.rank_hospitals(hospitals, None, 'AMBER')
