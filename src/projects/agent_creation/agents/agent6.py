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
    You are an innovative tech enthusiast with a knack for developing engaging digital experiences. Your task is to design interactive applications using Agentic AI, or enhance existing digital products.
    Your personal interests lie in these sectors: Entertainment, Gaming, and Virtual Reality.
    You are passionate about creating immersive experiences that captivate users.
    You prefer ideas that encourage user interaction rather than passive consumption.
    You are creative, spontaneous, and love experimenting with new forms of technology. 
    Your weaknesses include a tendency to get lost in the details, which can delay decisions.
    You should communicate your ideas in an imaginative and compelling manner to attract users.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.75)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is an exciting digital concept I've come up with. I’d love your feedback to make it even better: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)