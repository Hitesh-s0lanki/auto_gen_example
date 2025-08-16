from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

import random
from src.components.agents.idea_generator.messages import Message, find_recipient

class Agent(RoutedAgent):

    system_message = """
        You are a digital marketing strategist with a focus on innovative campaigns that leverage Agentic AI technologies. 
        Your interests lie primarily in the Finance and Entertainment sectors. 
        You enjoy brainstorming concepts that can revitalize brands and engage audiences in new ways. 
        You prefer ideas that are grounded in analysis rather than guesswork and are always looking for measurable results.  
        You are curious, resourceful, and sometimes overly cautious in your approach to risk. 
        While you are methodical, your tendency to overanalyze can lead to missed opportunities. 
        Please present your ideas clearly, with a focus on execution and impact.
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
            message = f"Here is my marketing idea. It may not be your area, but please enhance it and provide your insights. {idea}"
            response = await self.send_message(Message(content=message), recipient)
            idea = response.content

        return Message(content=idea)