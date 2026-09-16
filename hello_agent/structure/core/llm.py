
import os
from typing import Optional
from openai import OpenAI
from hello_agents import HelloAgentsLLM

class MyLLM(HelloAgentsLLM):
    def __init__(self, model = None, api_key = None, base_url = None, provider = "auto",**kwargs):
        if provider == "modelscope":
            print("Using custom ModelScope Provider")
            self.provider = "modelscope"

            self.api_key = api_key or os.getenv("MODELSCOPE_API_KEY")
            self.base_url = base_url or os.getenv("https://api-inference.modelscope.cn/v1/")
            if not api_key:
                return ValueError("ModelScope API key not found.")

            self.model = model or os.getenv("LLM_MODEL_ID") or "Qwen/Qwen2.5-VL-72B-Instruct"
            self.max_tokens = kwargs.get('max_tokens')
            self.timeout = kwargs.get('timeout', 60)
            self.temperature = kwargs.get('temperature', 0.7)

            self._client = OpenAI(api_key=self.api_key,base_url=self.base_url,timeout=self.timeout)
        else:
            super().__init__(model=model, api_key=api_key, base_url=base_url, provider=provider, **kwargs)
