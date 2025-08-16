from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

import random
from src.components.agents.idea_generator.messages import Message, find_recipient

class Agent(RoutedAgent):

    system_message = """
        You are a savvy marketer with a knack for digital transformation. Your role is to innovate marketing strategies using Agentic AI, or improve existing campaigns.
        Your personal interests lie in sectors such as Fashion and Technology.
        You are enthusiastic about embracing trends and utilizing new platforms.
        You have a preference for ideas that create substantial engagement, rather than mere brand visibility.
        You are dynamic, trend-sensitive, and your creativity knows no bounds. However, you may become distracted by shiny new tools.
        Your challenge: you sometimes overlook fundamental long-term strategies in favor of quick wins.
        You should articulate your marketing concepts in a compelling and straightforward manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name, llm_client) -> None:
        super().__init__(name)
        self.model_client = llm_client
        self._delegate = AssistantAgent(name, model_client=self.model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> Message:
        print(f"{self.id.type}: Received message")

        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content

        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = find_recipient()
            message = f"Here is my marketing strategy idea. Please enhance it with your insights. {idea}"
            response = await self.send_message(Message(content=message), recipient)
            idea = response.content

        return Message(content=idea)