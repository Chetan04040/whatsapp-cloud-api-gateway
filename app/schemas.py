from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# Outbound Message Schemas
class TextMessageRequest(BaseModel):
    to: str = Field(..., description="Recipient phone number with country code, e.g. 919876543210")
    message: str = Field(..., description="Text content to send")
    preview_url: bool = Field(default=False, description="Enable link preview")


class ButtonItem(BaseModel):
    id: str = Field(..., description="Unique callback ID for the button")
    title: str = Field(..., max_length=20, description="Button label (max 20 chars)")


class QuickReplyRequest(BaseModel):
    to: str = Field(..., description="Recipient phone number")
    body_text: str = Field(..., description="Message body introducing the quick actions")
    buttons: List[ButtonItem] = Field(..., min_length=1, max_length=3, description="1 to 3 quick reply buttons")


class ListRow(BaseModel):
    id: str = Field(..., description="Unique row identifier")
    title: str = Field(..., max_length=24, description="Title of the option")
    description: Optional[str] = Field(default=None, max_length=72, description="Short detail")


class ListSection(BaseModel):
    title: str = Field(..., description="Section header")
    rows: List[ListRow] = Field(..., description="Options in this section")


class ListMessageRequest(BaseModel):
    to: str = Field(..., description="Recipient phone number")
    header_text: Optional[str] = Field(default=None, description="Optional header")
    body_text: str = Field(..., description="Main prompt text")
    footer_text: Optional[str] = Field(default=None, description="Optional footer note")
    button_label: str = Field(default="Select Option", description="Label for the menu button")
    sections: List[ListSection] = Field(..., description="Sections and items")


# Webhook Verification Schema
class WebhookVerification(BaseModel):
    hub_mode: str = Field(alias="hub.mode")
    hub_verify_token: str = Field(alias="hub.verify_token")
    hub_challenge: str = Field(alias="hub.challenge")


# Generic Response
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
