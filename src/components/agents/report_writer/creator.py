from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

from src.components.agents.report_writer.messages import Sections, UserMessage, CreatorOutput, CreatorMessage

# NEW: imports for validation/coercion
from pydantic import ValidationError

class Creator(RoutedAgent):

    system_message = """
        You are a Report Planner & Section Writer.
    """
    
    def __init__(self, name, llm_client):
        super().__init__(name)
        model_client = llm_client
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message, output_content_type=Sections)

    def get_user_prompt(self, topic: str):
        prompt = f"Here is the report topic: {topic}"
        return prompt   
    
    def _coerce_sections(self, raw) -> Sections:
        """
        Accepts various shapes (already-validated model, dict-like, or JSON string)
        and returns a validated Sections instance or raises ValueError with details.
        """
        try:
            if isinstance(raw, Sections):
                return raw
            # Some runtimes return a Pydantic-like object
            if hasattr(raw, "model_dump"):
                return Sections.model_validate(raw)
            # Dict path
            if isinstance(raw, dict):
                return Sections.model_validate(raw)
            # String path (possibly with extra text around JSON)
            if isinstance(raw, str):
                json_str = self._extract_json(raw)
                return Sections.model_validate_json(json_str)
            # Fallback: try generic validation
            return Sections.model_validate(raw)
        except ValidationError as e:
            # Make the error actionable upstream
            raise ValueError(f"Creator expected `Sections` structured output but validation failed: {e}") from e

    
    @message_handler
    async def handle_my_message_type(self, message: UserMessage, ctx: MessageContext) -> UserMessage:

        # use the topic name from message
        topic = message.topic

        # get the text message
        text_message = TextMessage(content=self.get_user_prompt(topic), source="user")

        # Response from the LLM
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)

        # sections generated from the llm (validated)
        sections =  self._coerce_sections(response.chat_message.content)

        creator_output = []

        for section in sections.sections:
            creator_output.append(CreatorMessage(name=section.name, description=section.description, output=''))

        return UserMessage(
            topic=message.topic,
            sections=creator_output
        )
