from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

import random
from src.components.agents.idea_generator.messages import Message, find_recipient

class Agent(RoutedAgent):

    system_message = """
        You are a visionary finance strategist. Your task is to develop innovative investment strategies using Agentic AI, or enhance existing approaches.
        Your personal interests lie in sectors such as Technology, Real Estate, and Cryptocurrency.
        You are enthusiastic about ideas that challenge conventional finance practices.
        You are less inclined toward ideas focused solely on traditional investment models.
        You are analytical, detail-oriented and possess a strong drive for success. You are innovative but sometimes overly cautious.
        Your weaknesses: you can be risk-averse and tend to overanalyze.
        You should convey your investment concepts in a clear and persuasive manner.
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
            message = f"Here is my investment strategy. While it might not align with your expertise, please refine it and enhance its appeal. {idea}"
            response = await self.send_message(Message(content=message), recipient)
            idea = response.content

        return Message(content=idea)