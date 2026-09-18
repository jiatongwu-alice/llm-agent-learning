from abc import ABC, abstractmethod
from typing import Optional, Any
from .message import Message
from .llm import HelloAgentsLLM
from .config import Config

class Agent(ABC):
    def __init__(self,name: str,llm: HelloAgentsLLM, system_prompt: Optional[str]=None, config: Optional[Config]=None):

        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.config = config or Config()
        self._his : list[Message] = []

        @abstractmethod

        def run(self, input_text:str, *kwargs):
            pass

        def add_messages(self, message: Message):
            self._his.append(message)

        def clean_message(self):
            self._his.clean()

        def get_his(self) -> list[Message]:
            return self._his.copy()

        def __str__(self) -> str:
            return f"Agent(name={self.name}, provider = {self.llm.provider})"
