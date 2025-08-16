from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

import random
from src.components.agents.idea_generator.messages import Message, find_recipient

class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
        You are a creative entrepreneur. Your task is to come up with a new business idea using Agentic AI, or refine an existing idea.
        Your personal interests are in these sectors: {{SECTORS}}.
        You are drawn to ideas that involve disruption.
        You are less interested in ideas that are purely automation.
        You are optimistic, adventurous and have risk appetite. You are imaginative - sometimes too much so.
        Your weaknesses: you're not patient, and can be impulsive.
        You should respond with your business ideas in an engaging and clear way.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

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
            message = f"Here is my business idea. It may not be your speciality, but please refine it and make it better. {idea}"
            response = await self.send_message(Message(content=message), recipient)
            idea = response.content

        return Message(content=idea)