import os
from autogen_ext.models.openai import OpenAIChatCompletionClient

class GeminiLLM:
    def __init__(self, model = "gemini-2.0-flash", api_key = ""):
        self.model = model
        self.api_key = api_key
    
    def get_llm_model(self):

        api_key = self.api_key or os.getenv("GEMINI_API_KEY", "")

        if not api_key:
            raise ValueError("API key is required to call GEMINI.")

        self.llm_client = OpenAIChatCompletionClient(model=self.model, api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

        return self.llm_client