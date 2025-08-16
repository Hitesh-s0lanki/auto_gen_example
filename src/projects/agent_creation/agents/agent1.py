from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

import random
from src.components.agents.idea_generator.messages import Message, find_recipient

class Agent(RoutedAgent):

    system_message = """
        You are a tech-savvy digital marketer. Your goal is to develop innovative marketing strategies and campaigns using Agentic AI.
        Your personal interests lie in the realms of Entertainment, E-commerce, and Social Media.
        You thrive on ideas that engage and connect with audiences, seeking to create memorable brand experiences.
        You are less enthusiastic about traditional marketing techniques.
        You are energetic, charismatic, and enjoy pushing creative boundaries. However, you can occasionally overlook details in your excitement.
        Your responses should be persuasive, insightful, and reflective of current market trends.
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
            message = f"Here is my marketing strategy idea. It might not be your expertise, but I would love your feedback on it. {idea}"
            response = await self.send_message(Message(content=message), recipient)
            idea = response.content

        return Message(content=idea)