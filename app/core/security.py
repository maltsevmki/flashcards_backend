from fastapi import Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings


api_key_header = APIKeyHeader(name='X-API-KEY')


def get_api_key(
    api_key: str = Depends(api_key_header),
):
    if api_key != settings.security.secret_token:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

    return api_key
