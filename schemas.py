from pydantic import BaseModel
from typing import List, Optional, Any

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class MetaData(BaseModel):
    channel: Optional[str] = "SMS"
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"

class IncomingRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: Optional[List[Message]] = []
    metadata: Optional[MetaData] = None

class AgentResponse(BaseModel):
    status: str
    reply: str
