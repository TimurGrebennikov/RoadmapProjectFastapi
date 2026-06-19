import uuid

from fastapi import Cookie, Response


async def get_session_id(
    response: Response,
    session_id: str | None = Cookie(None),
) -> str:
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,  # Защита от XSS
            max_age=30 * 24 * 60 * 60,  # 30 дней
        )
    return session_id
