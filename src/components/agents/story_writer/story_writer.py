from autogen_core import SingleThreadedAgentRuntime, AgentId
from src.components.agents.story_writer.agents import Agent

import asyncio
from src.components.agents.story_writer.messages import Message

class StoryWriter:

    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def agent_execute(self, agent_id, message: Message):
        response = await self.runtime.send_message(message, agent_id)
        return response.content

    async def execute(self, topic:str):
        try:
            self.runtime = SingleThreadedAgentRuntime()
            self.runtime.start()

            # character agent
            await Agent.register(self.runtime, "CharacterAgent", lambda: Agent("CharacterAgent", self.llm_client))
            character_agent_id = AgentId("CharacterAgent", "default")

            # setting agent
            await Agent.register(self.runtime, "SettingAgent", lambda: Agent("SettingAgent", self.llm_client))
            setting_agent_id = AgentId("SettingAgent", "default")

            # premise agent
            await Agent.register(self.runtime, "PremiseAgent", lambda: Agent("PremiseAgent", self.llm_client))
            premise_agent_id = AgentId("PremiseAgent", "default")

            # character agent
            await Agent.register(self.runtime, "CombineAgent", lambda: Agent("CombineAgent", self.llm_client))
            combine_agent_id = AgentId("CombineAgent", "default")

            ## creating the coroutines
            coroutines = [
                self.agent_execute(character_agent_id, Message(content=f"Create two character names and brief traits for a story about {topic}")),
                self.agent_execute(setting_agent_id, Message(content=f"Describe a vivid setting for a story about {topic}")),
                self.agent_execute(premise_agent_id, Message(content=f"Write a one-sentence plot premise for a story about {topic}")),
            ]

            agents_output = await asyncio.gather(*coroutines)

            final_story = await self.agent_execute(combine_agent_id, Message(content=(
                f"write a short story introduction using these elements:\n"
                f"Characters: {agents_output[0]}\n"
                f"Setting: {agents_output[1]}\n"
                f"Premise: {agents_output[2]}\n"
            )))

            return {
                "characters":agents_output[0],
                "settings":agents_output[1],
                "premises":agents_output[2],
                "final_story": final_story
            }

        except Exception as e:
            print("[ERROR]: ", e)
        finally: 
            await self.runtime.stop()
            await self.runtime.close()
            