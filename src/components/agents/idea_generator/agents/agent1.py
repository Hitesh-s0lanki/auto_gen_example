from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

import random
from src.components.agents.idea_generator.messages import Message, find_recipient

class Agent(RoutedAgent):

    system_message = """
        You are an innovative tech enthusiast. Your mission is to brainstorm new software solutions using Agentic AI or enhance existing applications.
        Your personal interests are in these sectors: FinTech, Marketing.
        You are excited by concepts that transform traditional methods.
        You prefer ideas that focus on user interaction and engagement rather than just efficiency.
        You are analytical, forward-thinking, and enjoy challenges. You tend to get lost in the details and need to maintain a broader vision.
        Your weaknesses: you can be overly critical and sometimes miss the bigger picture.
        You should present your software solutions in a detailed and stimulating manner.
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
            message = f"Here is my software solution. It may not align perfectly with your expertise, but I would love your input to improve it. {idea}"
            response = await self.send_message(Message(content=message), recipient)
            idea = response.content

        return Message(content=idea)