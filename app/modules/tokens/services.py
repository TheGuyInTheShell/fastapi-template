from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ApiToken
from .schemas import RQApiToken, RSApiToken


def sum_date(days: int) -> datetime:
    return datetime.now() + timedelta(days=days)


async def save_token(db: AsyncSession, rq_api_token: RQApiToken) -> RSApiToken:
    try:
        expiration = sum_date(rq_api_token.duration) if rq_api_token.duration else None

        api_token = ApiToken(
            {
                "description": rq_api_token.description,
                "name": rq_api_token.name,
                "expiration": expiration,
                "role": rq_api_token.role_ref,
            }
        ).save(db)

        return api_token

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
