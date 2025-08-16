import streamlit as st
from src.components.ui.load_ui import LoadStreamlitUI

def load_app():
    # load Ui 
    ui = LoadStreamlitUI()
    user_controls, user_input = ui.load_streamlit_ui()

    if st.session_state.get("is_fetch_button_clicked", False):
        user_input = user_controls['time_frame']

    # Only proceed if user has entered a prompt and clicked Submit
    if user_input:
        try:
            usecase = user_controls.get("usecase", "")
            if not usecase:
                raise ValueError("Use Case is not define")
            

        except ValueError as ve:
            # LLM initialization or validation error
            st.error(str(ve))
        except Exception as e:
            # Catch-all for unexpected exceptions
            st.error(f"Unexpected error: {e}")