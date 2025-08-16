from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

class ColdEmailWriter:
    """
        Minimal cold email generator.
        User provides a single text brief; returns a short cold email.
    """

    SYSTEM_MESSAGE = (
        "You are a concise B2B cold email writer.\n"
        "Write ONE plain-text first-touch email based ONLY on the user's brief.\n"
        "Rules:\n"
        "- Start with: 'Subject: ...' on the first line.\n"
        "- 80–120 words total.\n"
        "- Friendly, specific, and low-pressure; 1 clear CTA.\n"
        "- If a name is given, use 'Hi <name>', else 'Hi there'.\n"
        "- No bold claims, no images, no attachments."
    )

    def __init__(self, llm_client):
        self.model_client = llm_client
        self.agent = AssistantAgent(
            name="cold_email_writer",
            model_client=self.model_client,
            system_message=self.SYSTEM_MESSAGE
        )

    async def execute(self, user_input: str) -> str:
        """ brief: a single text input from the user describing recipient, offer, and context. """
        msg = TextMessage(content=user_input.strip(), source="user")
        resp = await self.agent.on_messages([msg], cancellation_token=CancellationToken())
        return resp.chat_message.content
