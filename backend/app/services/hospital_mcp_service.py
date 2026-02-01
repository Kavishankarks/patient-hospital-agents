from __future__ import annotations
from typing import Any
import httpx
import json
from pathlib import Path

from app.core.config import settings

class HospitalMCPService:
    def __init__(self) -> None:
        self.base_url = settings.MCP_HOSPITAL_BASE_URL.rstrip('/')

    async def search(self, location: str, radius_km: int, specialty_needed: str | None, urgency: str) -> list[dict]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{self.base_url}/search", json={
                    'location': location,
                    'radius_km': radius_km,
                    'specialty_needed': specialty_needed,
                    'urgency': urgency,
                })
                resp.raise_for_status()
                return resp.json().get('hospitals', [])
        except Exception:
            mock_path = Path(__file__).with_name('mock_hospitals.json')
            data = json.loads(mock_path.read_text())
            return data.get('hospitals', [])

    async def capabilities(self, hospital_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/capabilities/{hospital_id}")
            resp.raise_for_status()
            return resp.json()

    def rank_hospitals(self, hospitals: list[dict], specialty_needed: str | None, urgency: str) -> list[dict]:
        ranked = []
        for h in hospitals:
            score = 0.0
            why = []
            if specialty_needed and specialty_needed in h.get('specialties', []):
                score += 3.0
                why.append('specialty match')
            if urgency == 'RED' and h.get('trauma_level', 0) >= 1:
                score += 3.0
                why.append('trauma-ready')
            score += max(0.0, 5.0 - float(h.get('eta_min', 60)) / 12.0)
            why.append('ETA considered')
            ranked.append({
                'hospital_id': h['id'],
                'name': h['name'],
                'score': round(score, 2),
                'why': why,
            })
        return sorted(ranked, key=lambda x: x['score'], reverse=True)[:5]
