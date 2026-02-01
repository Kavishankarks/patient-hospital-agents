from fastapi import Header, HTTPException

API_KEY_HEADER = 'X-API-Key'

async def api_key_guard(x_api_key: str | None = Header(default=None)) -> None:
    # Hackathon placeholder: accept if header present
    if x_api_key is None:
        raise HTTPException(status_code=401, detail='Missing API key')
