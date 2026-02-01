from fastapi import APIRouter
from app.api.v1.routes import patients, ingestion, profiling, questionnaire, intelligence, hospitals, medications, coach, feedback, auth

api_router = APIRouter()
api_router.include_router(patients.router, prefix='/patients', tags=['patients'])
api_router.include_router(ingestion.router, prefix='/patients', tags=['ingestion'])
api_router.include_router(profiling.router, prefix='/patients', tags=['profiling'])
api_router.include_router(questionnaire.router, prefix='/patients', tags=['questionnaire'])
api_router.include_router(intelligence.router, prefix='/patients', tags=['intelligence'])
api_router.include_router(hospitals.router, prefix='/patients', tags=['hospitals'])
api_router.include_router(medications.router, prefix='/patients', tags=['medications'])
api_router.include_router(coach.router, prefix='/patients', tags=['coach'])
api_router.include_router(feedback.router, prefix='/patients', tags=['feedback'])
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
