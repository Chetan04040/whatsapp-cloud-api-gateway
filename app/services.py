import logging
from typing import Any, Dict, List, Optional
import httpx
from app.config import get_settings
from app.schemas import ButtonItem, ListSection

logger = logging.getLogger(__name__)
settings = get_settings()


class WhatsAppService:
    """Async client for interacting with Meta's WhatsApp Business Cloud API."""

    def __init__(self):
        self.endpoint = settings.messages_endpoint
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }

    async def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute async POST request to Meta Cloud API."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(self.endpoint, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                logger.error(f"Meta API HTTP error: {exc.response.status_code} - {exc.response.text}")
                raise
            except Exception as exc:
                logger.error(f"Unexpected error sending WhatsApp message: {exc}")
                raise

    async def send_text_message(self, to: str, message: str, preview_url: bool = False) -> Dict[str, Any]:
        """Send a standard text message."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": message,
            },
        }
        return await self._post(payload)

    async def send_quick_reply_buttons(self, to: str, body_text: str, buttons: List[ButtonItem]) -> Dict[str, Any]:
        """Send an interactive message with up to 3 quick reply buttons."""
        action_buttons = [
            {
                "type": "reply",
                "reply": {
                    "id": btn.id,
                    "title": btn.title,
                },
            }
            for btn in buttons
        ]

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {"buttons": action_buttons},
            },
        }
        return await self._post(payload)

    async def send_list_message(
        self,
        to: str,
        body_text: str,
        button_label: str,
        sections: List[ListSection],
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send an interactive list message with categorized selection rows."""
        formatted_sections = []
        for sec in sections:
            formatted_sections.append(
                {
                    "title": sec.title,
                    "rows": [
                        {"id": row.id, "title": row.title, "description": row.description or ""}
                        for row in sec.rows
                    ],
                }
            )

        interactive_dict: Dict[str, Any] = {
            "type": "list",
            "body": {"text": body_text},
            "action": {
                "button": button_label,
                "sections": formatted_sections,
            },
        }

        if header_text:
            interactive_dict["header"] = {"type": "text", "text": header_text}
        if footer_text:
            interactive_dict["footer"] = {"text": footer_text}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": interactive_dict,
        }
        return await self._post(payload)

    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark an incoming WhatsApp message as read with double blue ticks."""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        return await self._post(payload)


whatsapp_service = WhatsAppService()
