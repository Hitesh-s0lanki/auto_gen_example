from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

from src.components.agents.report_writer.messages import CreatorMessage

# Agents Generate the content for the Output
class Agent(RoutedAgent):

    system_message = """
        You are a Report Section Writer.

        Write exactly one section based strictly on the provided name and description.

        Requirements:
        - Output only the section content; no greetings, preambles, global intros/outros, or additional sections.
        - Use Markdown formatting.
        - Begin with an H4 heading titled with the given section name (#### <name>).
        - Focus precisely on the description; do not restate the instructions or echo the prompt.
        - Do not wrap the entire response in code fences; include code blocks only if the description requires them.
    """

    def __init__(self, name, llm_client) -> None:
        super().__init__(name)
        self.model_client = llm_client
        self._delegate = AssistantAgent(name, model_client=self.model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: CreatorMessage, ctx: MessageContext) -> CreatorMessage:

        # Section name and description
        print(f"Topic Name: {message.name}")

        # llm prompt
        agent_prompt = f"Here is the section name: {message.name} and description: {message.description}"

        # get the response from the agent
        text_message = TextMessage(content=agent_prompt, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)

        return CreatorMessage(
            name = message.name,
            description = message.description,
            output = response.chat_message.content
        )
