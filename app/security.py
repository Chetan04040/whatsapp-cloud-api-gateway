import hmac
import hashlib
from typing import Optional
from fastapi import HTTPException, Header, Request, status
from app.config import get_settings

settings = get_settings()


def verify_signature(payload: bytes, signature_header: Optional[str]) -> bool:
    """Validate incoming payload with Meta's SHA-256 HMAC signature.

    Meta sends: X-Hub-Signature-256: sha256=<hash>
    """
    if not settings.APP_SECRET:
        # If APP_SECRET is not configured in dev/testing, skip validation with a warning
        return True

    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected_hash = signature_header.split("sha256=")[1]
    computed_hash = hmac.new(
        key=settings.APP_SECRET.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_hash, computed_hash)


async def validate_webhook_signature(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
) -> None:
    """FastAPI dependency to enforce Meta webhook signature verification."""
    raw_body = await request.body()
    if not verify_signature(raw_body, x_hub_signature_256):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid payload signature. Verification failed.",
        )
