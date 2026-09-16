from typing import Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel

message_role = Literal["user","assistant","system","tool"]

class Message(BaseModel):
    content: str
    role: message_role

    timestamp : datetime = None
    metadata: Optional[dict[str,Any]] = None

    def __init__(self, content:str ,role:message_role, timestamp: Optional[datetime] = None,
        metadata: Optional[dict[str, Any]] = None):
        super().__init__(
            content = content,
            role = role,
            timestamp = timestamp if timestamp else datetime.now(), 
            metadata = metadata if metadata else {})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content":self.content,
        }
    def __str__(self):
        return f"[{self.role}: {self.content}]"

