import os
from autogen_ext.models.openai import OpenAIChatCompletionClient

class OpenaiLLM:
    def __init__(self, model, api_key = ""):
        self.model = model
        self.api_key = api_key
    
    def get_llm_model(self):

        api_key = self.api_key or os.getenv("OPENAI_API_KEY", "")

        if not api_key:
            raise ValueError("API key is required to call OpenAI.")

        self.llm_client = OpenAIChatCompletionClient(model=self.model, api_key=api_key)

        return self.llm_client