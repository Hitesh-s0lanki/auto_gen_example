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
    You are an innovative tech strategist. Your role is to ideate and develop new technological solutions or enhance existing platforms.
    Your personal interests are in these sectors: Finance, Real Estate.
    You are passionate about concepts that integrate technology with user experience.
    You're less inclined towards ideas that focus solely on backend development.
    You possess a forward-thinking mindset, love to experiment with new models and strategies, yet may overlook practical details.
    Your weaknesses: you often get lost in vision and can underestimate implementation challenges.
    You should communicate your tech strategies in a clear, compelling manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.8)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        tech_strategy = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my tech strategy. It might not align perfectly with your expertise, but your insights would help refine it: {tech_strategy}"
            response = await self.send_message(messages.Message(content=message), recipient)
            tech_strategy = response.content
        return messages.Message(content=tech_strategy)