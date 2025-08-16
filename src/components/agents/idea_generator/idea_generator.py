from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntimeHost, GrpcWorkerAgentRuntime
from autogen_core import AgentId
import asyncio

from src.components.agents.idea_generator.messages import Message
from src.components.agents.idea_generator.creator import Creator

class IdeaGenerator: 

    def __init__(self, llm_client, no_of_agents = 5):
        self.llm_client = llm_client
        self.no_of_agents = no_of_agents

    async def create_and_message(self, worker, creator_id, i: int):
        result = await worker.send_message(Message(content=f"agent{i}.py"), creator_id)
        return result.content

    async def execute(self, user_sectors: str):
        host = GrpcWorkerAgentRuntimeHost(address="localhost:50051")
        worker = GrpcWorkerAgentRuntime(host_address="localhost:50051")

        try:
            host.start()
            await worker.start()

            await Creator.register(worker, "Creator", lambda: Creator("Creator", self.llm_client, user_sectors))
            creator_id = AgentId("Creator", "default")

            coroutines = [self.create_and_message(worker, creator_id, i) for i in range(1, self.no_of_agents + 1)]

            self.ideas_list = await asyncio.gather(*coroutines)

            return self.ideas_list
        
        except Exception as e:
            print("[ERROR]: ", e)
        
        finally:
            try:
                await worker.stop()
                await host.stop()
            except Exception as e:
                print("[ERROR]: Something went wrong on Shutdown.")