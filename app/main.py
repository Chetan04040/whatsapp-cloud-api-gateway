import logging
from typing import Any, Dict
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.schemas import (
    APIResponse,
    ListMessageRequest,
    QuickReplyRequest,
    TextMessageRequest,
)
from app.security import validate_webhook_signature
from app.services import whatsapp_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("whatsapp-gateway")
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready FastAPI Webhook Gateway & Message Engine for Meta WhatsApp Business Cloud API.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check():
    """System health check and configuration verification."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "api_version": settings.API_VERSION,
        "phone_number_id_configured": bool(settings.PHONE_NUMBER_ID),
        "app_secret_configured": bool(settings.APP_SECRET),
    }


@app.get("/webhook", tags=["Webhook"])
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
):
    """Handle Meta's Webhook Subscription Verification (hub.challenge challenge-response)."""
    if hub_mode == "subscribe" and hub_verify_token == settings.VERIFY_TOKEN:
        logger.info("Webhook verification challenge accepted.")
        return Response(content=hub_challenge, media_type="text/plain", status_code=status.HTTP_200_OK)

    logger.warning(f"Webhook verification failed. Token mismatch: {hub_verify_token}")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token mismatch.")


@app.post("/webhook", tags=["Webhook"], dependencies=[Depends(validate_webhook_signature)])
async def process_webhook(request: Request):
    """Receive and parse incoming WhatsApp Cloud API events (messages, read receipts, delivery statuses)."""
    payload: Dict[str, Any] = await request.json()
    logger.info(f"Incoming WhatsApp webhook payload: {payload}")

    # Parse entries safely
    entries = payload.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})

            # 1. Handle incoming user messages
            if "messages" in value:
                for msg in value["messages"]:
                    msg_id = msg.get("id")
                    from_user = msg.get("from")
                    msg_type = msg.get("type")
                    logger.info(f"Received message [{msg_type}] from {from_user} (ID: {msg_id})")

                    # Automatically mark message as read
                    if msg_id and settings.WHATSAPP_TOKEN:
                        try:
                            await whatsapp_service.mark_as_read(msg_id)
                        except Exception as e:
                            logger.error(f"Failed to mark message as read: {e}")

            # 2. Handle delivery and read receipts
            if "statuses" in value:
                for st in value["statuses"]:
                    status_type = st.get("status")
                    recipient_id = st.get("recipient_id")
                    logger.info(f"Status update: {status_type} for recipient {recipient_id}")

    return {"status": "success", "processed": True}


@app.post("/api/v1/messages/text", response_model=APIResponse, tags=["Outbound Messaging"])
async def send_text(req: TextMessageRequest):
    """Send a plain text message via Meta Cloud API."""
    try:
        res = await whatsapp_service.send_text_message(
            to=req.to,
            message=req.message,
            preview_url=req.preview_url,
        )
        return APIResponse(success=True, message="Message dispatched successfully", data=res)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@app.post("/api/v1/messages/quick-replies", response_model=APIResponse, tags=["Outbound Messaging"])
async def send_quick_replies(req: QuickReplyRequest):
    """Send an interactive quick-reply button message (up to 3 action buttons)."""
    try:
        res = await whatsapp_service.send_quick_reply_buttons(
            to=req.to,
            body_text=req.body_text,
            buttons=req.buttons,
        )
        return APIResponse(success=True, message="Quick reply buttons dispatched", data=res)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@app.post("/api/v1/messages/list", response_model=APIResponse, tags=["Outbound Messaging"])
async def send_list_message(req: ListMessageRequest):
    """Send an interactive dropdown selection list menu."""
    try:
        res = await whatsapp_service.send_list_message(
            to=req.to,
            body_text=req.body_text,
            button_label=req.button_label,
            sections=req.sections,
            header_text=req.header_text,
            footer_text=req.footer_text,
        )
        return APIResponse(success=True, message="List message dispatched", data=res)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
