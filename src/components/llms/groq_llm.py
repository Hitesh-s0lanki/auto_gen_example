import os
from autogen_ext.models.openai import OpenAIChatCompletionClient

class GroqLLM:
    def __init__(self, model = "llama-3.3-70b-versatile", api_key = ""):
        self.model = model
        self.api_key = api_key
    
    def get_llm_model(self):

        api_key = self.api_key or os.getenv("GROQ_API_KEY", "")

        if not api_key:
            raise ValueError("API key is required to call Groq.")

        self.llm_client = OpenAIChatCompletionClient(model=self.model, api_key=api_key, base_url="https://api.groq.com/openai/v1")

        return self.llm_client