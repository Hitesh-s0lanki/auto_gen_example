from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntimeHost, GrpcWorkerAgentRuntime
from autogen_core import AgentId
import asyncio

from src.components.agents.report_writer.creator import Creator
from src.components.agents.report_writer.agent import Agent
from src.components.agents.report_writer.messages import UserMessage, CreatorMessage

class ReportWriter:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def worker_agents(self, worker, recipient_id, message: CreatorMessage):
        result = await worker.send_message(message, recipient_id)
        return result.output

    async def execute(self, user_input: str):
        host = GrpcWorkerAgentRuntimeHost(address="localhost:50051")
        worker = GrpcWorkerAgentRuntime(host_address="localhost:50051")

        try:
            host.start()
            await worker.start()

            # Register agents
            await Creator.register(worker, "Creator", lambda: Creator("Creator", self.llm_client))
            creator_id = AgentId("Creator", "default")

            await Agent.register(worker, "ContentAgent", lambda: Agent("ContentAgent", self.llm_client))
            content_agent_id = AgentId("ContentAgent", "default")

            # Ask Creator to plan sections
            sections = await worker.send_message(UserMessage(topic=user_input, sections=[]), creator_id)

            coroutines = [
                self.worker_agents(
                    worker = worker,
                    recipient_id = content_agent_id,
                    message = CreatorMessage(name = section["name"], description = section["description"], output = '')
                )
                for section in sections.sections
            ]

            outputs = await asyncio.gather(*coroutines)

            # Now form the proper output
            # Format completed section to str to use as context for final sections
            self.completed_report_sections = "\n\n---\n\n".join(outputs)

            return self.completed_report_sections
        
        except Exception as e:
            print("[ERROR]: ", e)
        
        finally:
            try:
                await worker.stop()
                await host.stop()
            except Exception as e:
                print("[ERROR]: Something went wrong on Shutdown.")
