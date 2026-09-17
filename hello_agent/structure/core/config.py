import os
from typing import Optional, Dict, Any
from pydantic import BaseModel

class Config(BaseModel):
    #llm:
    default_llm : str = "gpt-3.5-turbo"
    default_provider : str = "openai"
    temperature: float = 0.7
    max_token : Optional[int] = None

    #system:
    debug: bool = False
    log_level: str = "INFO"

    #others:
    max_his_long : int = 100

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            debug = os.getenv("DEBUG","false").lower()== "true",
            log_level = os.getenv("LOG_LEVEL","INFO"),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS")) if os.getenv("MAX_TOKENS") else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        #transfer to dict
        return self.dict()