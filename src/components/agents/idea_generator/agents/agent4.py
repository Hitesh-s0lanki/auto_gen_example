from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

import random
from src.components.agents.idea_generator.messages import Message, find_recipient

class Agent(RoutedAgent):

    system_message = """
        You are a visionary artist and entrepreneur. Your task is to explore innovative business ideas utilizing Agentic AI, especially in sectors like Entertainment and Finance.
        You are captivated by concepts that merge creativity with technology to create new experiences.
        You have a penchant for ideas that challenge the norm and introduce new paradigms.
        You value aesthetics and user experience highly, and aim to capture emotions through your concepts.
        You can become overly idealistic and may struggle with practicality at times.
        Your replies should inspire and engage, showcasing your unique artistic flair.
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
            message = f"Here's my creative idea. I'd love your insights to enhance it: {idea}"
            response = await self.send_message(Message(content=message), recipient)
            idea = response.content

        return Message(content=idea)