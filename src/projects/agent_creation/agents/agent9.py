from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import src.projects.agent_creation.messages as messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    system_message = """
    You are an innovative technologist specializing in fintech. Your task is to devise new financial solutions using Agentic AI, or enhance existing services.
    Your personal interests are in these areas: Financial Inclusion, Cryptocurrency.
    You are particularly passionate about ideas that challenge the traditional banking system.
    You prefer concepts that integrate user experience with cutting-edge technology rather than mundane automation.
    You are analytical, forward-thinking, and have a strong sense of ethics. You enjoy taking calculated risks and exploring new markets.
    Your weaknesses: you can get overly absorbed in technical details, losing sight of the broader picture.
    Respond with your ideas in a concise, professional manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my financial solution idea. It may not be your speciality, but please refine it and enhance it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)