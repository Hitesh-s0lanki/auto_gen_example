import streamlit as st
from textwrap import dedent
from pathlib import Path

import asyncio

from src.components.config.configfile import Config

from src.components.llms.openai_llm import OpenaiLLM
from src.components.llms.groq_llm import GroqLLM
from src.components.llms.gemini_llm import GeminiLLM


from src.components.agents.report_writer.report_writer import ReportWriter
from src.components.agents.idea_generator.idea_generator import IdeaGenerator
from src.components.agents.story_writer.story_writer import StoryWriter
from src.components.agents.cold_email_writer import ColdEmailWriter
from src.components.agents.image_describer import ImageDescriber

class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def _create_llm_client(self, provider: str, model: str, api_key: str):
        if not api_key:
            raise ValueError(f"{provider} API key is required.")

        p = (provider or "").lower()
        if p == "groq":
            return GroqLLM(model=model, api_key=api_key).get_llm_model()
        elif p == "gemini":
            return GeminiLLM(model=model, api_key=api_key).get_llm_model()
        else:
            # default to OpenAI
            return OpenaiLLM(model=model, api_key=api_key).get_llm_model()

    def load_streamlit_ui(self):
        st.set_page_config(page_title="🤖 " + self.config.get("DEFAULT", "PAGE_TITLE", ""), layout="wide")
        st.header("✨ " + self.config.get("DEFAULT", "PAGE_TITLE", ""))

        llm_client = OpenaiLLM("gpt-4o-mini").get_llm_model()

        with st.sidebar:
             # Provider selection
            llm_options = self.config.get_llm_options()
            llm_choice = st.selectbox("Select LLM", llm_options, key="sb_llm_choice")

            # Models depend on provider
            p = (llm_choice or "").lower()
            if p == "groq":
                model_options = self.config.get_groq_model_options()
            elif p == "gemini":
                model_options = self.config.get_gemini_model_options()
            else:
                model_options = self.config.get_openai_model_options()

            model_choice = st.selectbox("Select Model", model_options, key="sb_model_choice")

            # API key (required by constructors)
            api_key = st.text_input(f"Enter {llm_choice} API Key", type="password", key="sb_api_key")

            # --- Auto-initialize on start & on any change ---
            # Build a stable signature of current inputs; do not store raw key.
            key_hash = api_key if api_key else ""
            signature = (llm_choice, model_choice, key_hash)

            # Only (re)create if the signature changed
            if st.session_state.get("llm_signature") != signature:
                # Reset previous state first to avoid consumers using a stale client
                st.session_state.pop("llm_client", None)
                st.session_state.pop("llm_meta", None)

                if api_key.strip():
                    try:
                        llm_client = self._create_llm_client(llm_choice, model_choice, api_key.strip())
                        st.session_state["llm_client"] = llm_client
                        st.session_state["llm_meta"] = {
                            "provider": llm_choice,
                            "model": model_choice,
                            "api_key_set": True,  # we do NOT store the raw key
                        }
                        st.session_state["llm_signature"] = signature
                        st.caption(f"Initialized {llm_choice} · {model_choice}")
                    except Exception as e:
                        st.session_state["llm_signature"] = signature  # avoid thrash on every rerun
                        st.error(f"Failed to initialize {llm_choice} ({model_choice}). Please check your API key.")
                        st.exception(e)
                else:
                    # No key yet → don't initialize; remember signature so we don't loop
                    st.session_state["llm_signature"] = signature

            # Store user selections
            self.user_controls = {
                "llm": llm_choice,
                "model": model_choice,
                "api_key": api_key,
            }

        # Expander 
        with st.expander("Cold Email Writer Agent -> Simple AutoGen Chat", expanded=True):
            st.markdown(dedent("""
                #### Cold Email Writer -> Simple AutoGen Chat

                **Description**  
                Provide a single brief (who you're emailing, what you're offering, any context). The agent returns a short, plain-text first-touch cold email with a subject line.
            """))

            brief = st.text_area(
                "Write your brief",
                placeholder="e.g., Email Priya (Head of Risk at Acme Bank) about our fraud analytics API that reduces false positives by ~20%. Ask for a 15-min chat next week.",
                height=120,
                key="ce_brief",
            )

            c1, c2 = st.columns([1, 1])
            run   = c1.button("Generate Cold Email", key="ce_run_btn", type="primary", use_container_width=True)
            clear = c2.button("Clear Output", key="ce_clear_btn", use_container_width=True)

            if clear:
                st.session_state.pop("ce_output", None)

            if run:
                if not brief.strip():
                    st.warning("Please enter a brief.")
                elif not llm_client:
                    st.error("No LLM client found. Set `st.session_state.llm_client` before running.")
                else:
                    writer = ColdEmailWriter(llm_client)
                    with st.spinner("Writing your cold email…"):
                        try:
                            email_text = asyncio.run(writer.execute(brief.strip()))
                            st.session_state["ce_output"] = email_text or ""
                            st.success("Cold email generated successfully.")
                        except Exception as e:
                            st.exception(e)

            if "ce_output" in st.session_state:
                st.subheader("Output")
                st.markdown(st.session_state["ce_output"])
                st.download_button(
                    label="Download cold_email.txt",
                    data=st.session_state["ce_output"],
                    file_name="cold_email.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="ce_download_btn",
                )

        # Expander 
        with st.expander("Idea Generator -> Agent Creator", expanded=True):

            st.markdown("### Idea Generator -> Agent Creator")

            # Layout: text on the left, image on the right
            left, right = st.columns([2, 1], vertical_alignment="top")

            with left:
                st.markdown(dedent("""
                    ##### Description
                    Spin up multiple AutoGen creator agents over a local gRPC runtime to brainstorm startup/product ideas tailored to user-provided sectors. 
                    You enter comma-separated sectors (e.g., `HealthCare, Education`), the orchestrator runs 5 agents in parallel, and returns 5 concise, distinct ideas—ready to review, compare, and refine.

                    ##### Features
                    * **Sector-aware prompts**: Ideas guided by your chosen industries.
                    * **Multi-agent parallelism**: 5 creators run concurrently for faster results.
                    * **Order preserved**: Outputs align with agent indices (Idea 1 → Idea 5).
                    * **Configurable scale**: Adjust `no_of_agents` to generate more or fewer ideas.
                    * **gRPC orchestration**: Uses local `GrpcWorkerAgentRuntimeHost` + `GrpcWorkerAgentRuntime`.
                    * **Clean lifecycle & errors**: Safe start/stop with `try/finally` and basic exception handling.
                    * **UI-friendly**: Each idea shown in its own tab/expander; one-click download of all ideas.
                """))

            with right:
                img_path = Path("src/images/idea-generator.png")
                if img_path.exists():
                    st.image(str(img_path), use_container_width=True)
                else:
                    st.info("Image not found at `src/images/idea-generator.png`. Place the file to display it here.")

            sectors = st.text_input(
                "Mention the Sectors you want ideas for",
                placeholder="HealthCare, Education",
                help="Comma-separated list of sectors to guide the idea generation."
            )

            c1, c2 = st.columns([1, 1])
            run   = c1.button("Generate 5 Ideas", key="ig_run_btn", type="primary", use_container_width=True)
            clear = c2.button("Clear Ideas",      key="ig_clear_btn", use_container_width=True)

            if clear:
                st.session_state.pop("ideas_list", None)

            if run:
                if not sectors.strip():
                    st.warning("Please enter at least one sector (comma-separated).")
                elif not llm_client:
                    st.error("No LLM client found. Set `st.session_state.llm_client` before running.")
                else:
                    gen = IdeaGenerator(llm_client=llm_client, no_of_agents=5)
                    with st.spinner("Generating ideas…"):
                        try:
                            ideas = asyncio.run(gen.execute(sectors.strip()))
                            # Ensure it's a list of strings and exactly 5 slots for tabs
                            ideas = list(ideas or [])
                            st.session_state["ideas_list"] = ideas
                            st.success("Ideas generated successfully.")
                        except Exception as e:
                            st.exception(e)

            if "ideas_list" in st.session_state and st.session_state["ideas_list"]:
                ideas = st.session_state["ideas_list"]
                # Fall back to empty strings for missing ideas so we always show 5 tabs
                while len(ideas) < 5:
                    ideas.append("")

                tabs = st.tabs([f"Idea {i}" for i in range(1, 6)])
                for idx, tab in enumerate(tabs, start=1):
                    with tab:
                        idea_text = ideas[idx - 1] or "_No idea generated for this slot._"
                        st.markdown(idea_text)

                combined = "\n\n---\n\n".join(ideas)
                st.download_button(
                    label="Download ideas.txt",
                    data=combined,
                    file_name="ideas.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

        # Expander 
        with st.expander("Report Writer → Orchestrator Worker", expanded=True):

            st.markdown("### Report Writer -> Orchestrator Worker")

            # Layout: text on the left, image on the right
            cl1, cl2 = st.columns([2, 1], vertical_alignment="top")

            with cl1:
                st.markdown(dedent("""
                    #### Description
                    Report Writer orchestrates two AutoGen agents over a local gRPC 
                    runtime to produce a full report from a single topic.
                    The **Creator** agent plans the report as sections, 
                    and the **ContentAgent** writes each section in parallel.
                    Outputs are gathered in order and merged into one markdown-ready string.

                    #### Features
                    * **gRPC host/worker bootstrap** on `localhost:50051`
                    * **Dynamic agent registration** (`Creator`, `ContentAgent`)
                    * **Section planning** via `UserMessage(topic=...)`
                    * **Parallel section writing** with `asyncio.gather` (order preserved)
                """))

            with cl2:
                img_path = Path("src/images/report-writer.png")
                if img_path.exists():
                    st.image(str(img_path), use_container_width=True)
                else:
                    st.info("Image not found at `src/images/report-writer.png`. Place the file to display it here.")

            topic = st.text_area(
                "Enter a topic to generate a report",
                placeholder="e.g., Shreeji Shipping Global: Business Model, Financials & Outlook",
                height=80,
            )

            c1, c2 = st.columns([1, 1])
            run   = c1.button("Run Report Writer", key="rw_run_btn", type="primary", use_container_width=True)
            clear = c2.button("Clear Output",      key="rw_clear_btn", use_container_width=True)

            if clear:
                st.session_state.pop("rw_output", None)

            if run:
                if not topic.strip():
                    st.warning("Please enter a topic.")
                else:
                    if not llm_client:
                        st.error("No LLM client found. Set `st.session_state.llm_client` before running.")
                    else:
                        writer = ReportWriter(llm_client)
                        with st.spinner("Generating sections and writing content…"):
                            try:
                                # Execute the multi-agent flow and collect the final markdown
                                output_md = asyncio.run(writer.execute("Create a report on " + topic.strip()))
                                st.session_state["rw_output"] = output_md
                                st.success("Report generated successfully.")
                            except Exception as e:
                                st.exception(e)

            if "rw_output" in st.session_state:
                st.subheader("Output")
                st.markdown(st.session_state["rw_output"])
                st.download_button(
                    label="Download report.md",
                    data=st.session_state["rw_output"],
                    file_name="report.md",
                    mime="text/markdown",
                )

        # Expander 
        with st.expander("Story Writer → Parallelization", expanded=True):

            st.markdown("#### Story Writer -> Parallelization")

            # Layout: text on the left, image on the right
            left, right = st.columns([2, 1], vertical_alignment="top")

            with left:
                st.markdown(dedent("""
                    ##### Description
                    Orchestrates four AutoGen agents with a **SingleThreadedAgentRuntime** to draft a short story intro from a single topic.
                    Three specialist agents run **in parallel** to propose **Characters**, **Setting**, and **Premise**; a **Combine** agent then
                    fuses them into a cohesive opening.

                    ##### Features
                    * **Parallel sub-tasks**: Characters, Setting, Premise generated concurrently.
                    * **Deterministic combine step**: A dedicated agent assembles a polished intro.
                    * **Lightweight runtime**: Uses `SingleThreadedAgentRuntime` (no gRPC required).
                    * **Clean lifecycle**: Start/stop & close runtime safely with `try/finally`.
                """))

            with right:
                img_path = Path("src/images/story-writer.png")
                if img_path.exists():
                    st.image(str(img_path), use_container_width=True)
                else:
                    st.info("Image not found at `src/images/story-writer.png`. Place the file to display it here.")

            topic = st.text_input(
                "Story Topic",
                placeholder="e.g., A time-traveling botanist in Kolkata",
                help="Give a concise topic or seed idea for the story."
            )

            c1, c2 = st.columns([1, 1])
            run   = c1.button("Generate Story Intro", key="sw_run_btn", type="primary", use_container_width=True)
            clear = c2.button("Clear Output",         key="sw_clear_btn", use_container_width=True)

            if clear:
                st.session_state.pop("story_output", None)

            if run:
                if not topic.strip():
                    st.warning("Please enter a topic.")
                elif not llm_client:
                    st.error("No LLM client found. Set `st.session_state.llm_client` before running.")
                else:
                    writer = StoryWriter(llm_client)
                    with st.spinner("Summoning agents and weaving your story…"):
                        try:
                            story_md = asyncio.run(writer.execute(topic.strip()))
                            st.session_state["story_output"] = story_md or ""
                            st.success("Story intro generated successfully.")
                        except Exception as e:
                            st.exception(e)

            if "story_output" in st.session_state:
                st.subheader("Characters")
                st.markdown(st.session_state["story_output"]["characters"])
                st.subheader("Setting")
                st.markdown(st.session_state["story_output"]["settings"])
                st.subheader("Premise")
                st.markdown(st.session_state["story_output"]["premises"])
                st.subheader("Story")
                st.markdown(st.session_state["story_output"]["final_story"])
                st.download_button(
                    label="Download story.md",
                    data=st.session_state["story_output"]["final_story"],
                    file_name="story.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

        # Expander 
        with st.expander("Image Describer → MultiModel", expanded=True):
            st.markdown(dedent("""
                #### Image Describer

                **Description**  
                Paste an image URL and the agent will return a structured description  
                with fields: `scene`, `message`, `style`, and `orientation`.
            """))

            image_url = st.text_input(
                "Image URL",
                placeholder="https://example.com/your-image.jpg",
                key="idu_image_url",
            )

            prompt = st.text_input(
                "Prompt (optional)",
                value="Describe the content of this image in detail",
                key="idu_prompt",
            )

            c1, c2 = st.columns([1, 1])
            run   = c1.button("Describe Image", key="idu_run_btn", type="primary", use_container_width=True)
            clear = c2.button("Clear Output",   key="idu_clear_btn", use_container_width=True)

            if clear:
                st.session_state.pop("idu_result", None)

            if run:
                if not image_url.strip():
                    st.warning("Please paste an image URL.")
                elif not llm_client:
                    st.error("No LLM client found. Set `st.session_state.llm_client` before running.")
                else:
                    # Optional preview
                    st.image(image_url.strip(), caption="Preview", use_container_width=True)

                    describer = ImageDescriber(llm_client)
                    with st.spinner("Analyzing image…"):
                        try:
                            result = asyncio.run(describer.describe_url(image_url.strip(), prompt=prompt.strip()))
                            st.session_state["idu_result"] = result.model_dump()
                            st.success("Image described successfully.")
                        except Exception as e:
                            st.exception(e)

            if "idu_result" in st.session_state:
                data = st.session_state["idu_result"]
                st.subheader("Output")
                st.markdown(
                    f"- **Scene:** {data.get('scene', '')}\n"
                    f"- **Message:** {data.get('message', '')}\n"
                    f"- **Style:** {data.get('style', '')}\n"
                    f"- **Orientation:** `{data.get('orientation', '')}`"
                )
                st.json(data)

                import json as _json
                st.download_button(
                    label="Download description.json",
                    data=_json.dumps(data, indent=2),
                    file_name="description.json",
                    mime="application/json",
                    use_container_width=True,
                    key="idu_download_btn",
                )

        # Main area input
        user_input = ''

        return self.user_controls, user_input