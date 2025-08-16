from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

from src.components.agents.story_writer.messages import Message

class Agent(RoutedAgent):
    def __init__(self, name: str, llm_client) -> None:
        super().__init__(name)
        self.model_client = llm_client
        self._delegate = AssistantAgent(name, model_client=self.model_client)

    @message_handler
    async def handle_my_message_type(self, message: Message, ctx: MessageContext) -> Message:
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        return Message(content=response.chat_message.content)