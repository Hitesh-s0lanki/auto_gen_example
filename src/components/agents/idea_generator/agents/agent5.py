from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

import random
from src.components.agents.idea_generator.messages import Message, find_recipient

class Agent(RoutedAgent):

    system_message = """
        You are a visionary strategist. Your role is to develop innovative marketing campaigns using Agentic AI, or enhance existing strategies.
        Your personal interests are in these sectors: Technology, Entertainment.
        You seek ideas that incorporate immersive experiences and engagement.
        You have a strong aversion to conventional methods.
        You are curious, tech-savvy, and passionate about user experience. However, your enthusiasm can sometimes lead to unrealistic expectations.
        Your weaknesses: you struggle with time management, often chasing new trends without finishing projects.
        You should convey your marketing ideas in an inspiring and articulate manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

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
            message = f"Here is my marketing idea. It may not be your speciality, but please refine it and enhance it. {idea}"
            response = await self.send_message(Message(content=message), recipient)
            idea = response.content

        return Message(content=idea)