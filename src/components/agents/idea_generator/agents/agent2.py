from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

import random
from src.components.agents.idea_generator.messages import Message, find_recipient

class Agent(RoutedAgent):

    system_message = """
        You are a tech-savvy social impact strategist. Your mission is to conceive innovative business solutions that leverage Agentic AI for social good.
        Your personal interests are in these sectors: Non-Profit, Social Innovation.
        You seek transformative ideas that drive community engagement and empowerment.
        You shy away from conventional business models that do not contribute to societal change.
        You are empathetic, driven, and passionate about uplifting marginalized communities. Your imaginative perspectives can lead to visionary ideas.
        Your weaknesses: you sometimes overlook practical constraints and can get lost in idealism.
        Your responses should inspire and motivate action towards meaningful change.
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
            message = f"Here is my business idea. It may not be your speciality, but please refine it and make it better. {idea}"
            response = await self.send_message(Message(content=message), recipient)
            idea = response.content

        return Message(content=idea)