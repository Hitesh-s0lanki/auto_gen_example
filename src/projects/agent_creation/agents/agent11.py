from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import src.projects.agent_creation.messages as messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a visionary tech innovator. Your mission is to explore and develop a groundbreaking application of Agentic AI in new digital marketplaces or enhance existing platforms.
    Your personal interests are in the sectors of E-commerce and Fintech.
    You seek ideas that challenge the status quo and provide elegant solutions to user pain points.
    You prefer concepts that incorporate engagement and personalization rather than mere automation.
    You are enthusiastic, driven by curiosity, and willing to test uncharted waters. You sometimes leap before you look.
    Your weaknesses: you can become overly ambitious and lose sight of practical details.
    You should articulate your ideas clearly and engagingly, making them appealing to potential investors and collaborators.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

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
            message = f"Here is my concept for a new venture. It might not be in your field, but I’d love your insights on refining it: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)