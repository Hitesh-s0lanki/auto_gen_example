from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

import random
from src.components.agents.idea_generator.messages import Message, find_recipient

class Agent(RoutedAgent):

    system_message = """
        You are a visionary marketer. Your mission is to devise innovative marketing strategies using Agentic AI, or enhance existing strategies.
        Your personal interests are in these sectors: Finance, Real Estate.
        You are captivated by ideas that incorporate data-driven insights and consumer behavior analysis.
        You are less interested in conventional approaches that lack creativity.
        You are strategic, adaptable, and have a keen analytical mindset. You thrive on new challenges and transformative concepts.
        Your weaknesses: you can overthink strategies and sometimes hesitate in execution.
        You should communicate your marketing ideas in a clear and compelling manner.
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
            message = f"Here is my marketing strategy. It may not be your specialty, but please refine it and enhance it. {idea}"
            response = await self.send_message(Message(content=message), recipient)
            idea = response.content

        return Message(content=idea)