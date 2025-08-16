from dotenv import load_dotenv
from src.components.main import load_app

load_dotenv(override=True)

if __name__ == "__main__":
    load_app()


# # if __name__ == "__main__":
# #     asyncio.run(main())

# if __name__ == "__main__":
#     ideas_list = all_as_list()
#     print(ideas_list)

# from dotenv import load_dotenv
# import asyncio

# from src.components.llms.openai_llm import OpenaiLLM
# from src.components.agents.report_writer.report_writer import ReportWriter

# load_dotenv(override=True)

# if __name__ == "__main__":

#     # llm model client
#     openai_llm = OpenaiLLM("gpt-4o-mini").get_llm_model()

#     asyncio.run(ReportWriter(openai_llm).execute("Create a report on Agentic AI RAGs."))