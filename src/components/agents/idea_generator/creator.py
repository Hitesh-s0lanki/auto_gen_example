from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

from src.components.agents.idea_generator.messages import Message

import importlib
from autogen_core import AgentId

class Creator(RoutedAgent):

    system_message = """
        You are an Agent that is able to create new AI Agents.
        You receive a template in the form of Python code that creates an Agent using Autogen Core and Autogen Agentchat.
        You should use this template to create a new Agent with a unique system message that is different from the template,
        and reflects their unique characteristics, interests and goals.
        You can choose to keep their overall goal the same, or change it.
        Don't Change the sector mentioned.
        You can choose to take this Agent in a completely different direction. The only requirement is that the class must be named Agent,
        and it must inherit from RoutedAgent and have an __init__ method that takes a name parameter.
        Also avoid environmental interests - try to mix up the business verticals so that every agent is different.
        Respond only with the python code, no other text, and no markdown code blocks.
    """

    def __init__(self, name, llm_client, sectors = "Healthcare, Education") -> None:
        super().__init__(name)
        self.model_client = llm_client
        self._delegate = AssistantAgent(name, model_client=self.model_client, system_message=self.system_message)
        self.sectors = sectors

    def get_user_prompt(self):
        prompt = "Please generate a new Agent based strictly on this template. Stick to the class structure. \
            Respond only with the python code, no other text, and no markdown code blocks.\n\n\
            Be creative about taking the agent in a new direction, but don't change method signatures.\n\n\
            Here is the template:\n\n"
        
        with open("src/components/agents/idea_generator/agent.py", "r", encoding="utf-8") as f:
            template = f.read()
        
        template = template.replace("{{SECTORS}}", self.sectors)

        return prompt + template   
        

    @message_handler
    async def handle_my_message_type(self, message: Message, ctx: MessageContext) -> Message:
        filename = message.content
        agent_name = filename.split(".")[0]

        text_message = TextMessage(content=self.get_user_prompt(), source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        
        with open(f"src/components/agents/idea_generator/agents/{filename}", "w", encoding="utf-8") as f:
            f.write(response.chat_message.content)

        print(f"** Creator has created python code for agent {agent_name} - about to register with Runtime")

        module = importlib.import_module(f"src.components.agents.idea_generator.agents.{agent_name}")
        await module.Agent.register(self.runtime, agent_name, lambda: module.Agent(agent_name, self.model_client))

        result = await self.send_message(Message(content="Give me an idea"), AgentId(agent_name, "default"))
        return Message(content=result.content)