import streamlit as st
from parlant.client import ParlantClient

def init_chat(agent_id: str):
    """Initializes chat session state with a specific agent ID.

    Args:
        agent_id (str): The ID of the agent to initialize the chat with.
    """
    # Reinitialize messages when switching agents
    if "current_agent_id" not in st.session_state or st.session_state.current_agent_id != agent_id:
        st.session_state.messages = []
        st.session_state.current_agent_id = agent_id

    if "parlant_session" not in st.session_state:
        client = ParlantClient(base_url="http://localhost:8800")
        try:
            agent = client.agents.retrieve(agent_id)
        except Exception as e:
            st.error(f"Error retrieving agent: {e}")
            return
        try:
            session = client.sessions.create(agent_id=agent_id, allow_greeting=False)
        except Exception as e:
            st.error(f"Error creating session: {e}")
            return
        st.session_state.parlant_session = session
        st.session_state.parlant_client = client


def show_chat(prompt_placeholder: str = "Ask me anything!", extra_info: str = ""):
    """Displays the chat interface with custom prompt placeholder and extra information.

    Args:
        prompt_placeholder (str): The placeholder text for the chat input.
        extra_info (str): Extra information to provide context to the AI.
    """
    st.markdown("---")
    st.subheader("Chat with AI Tutor")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(prompt_placeholder):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        try:
            customer_event = st.session_state.parlant_client.sessions.create_event(
                session_id=st.session_state.parlant_session.id,
                source="customer",
                kind="message",
                message=prompt,
                extra_info = extra_info,
            )
        except Exception as e:
            st.error(f"Error sending message: {e}")
            return

        try:
            agent_event, *_ = st.session_state.parlant_client.sessions.list_events(
                session_id=st.session_state.parlant_session.id,
                source="ai_agent",
                kinds="message",
                min_offset=customer_event.offset,
            )
        except Exception as e:
            st.error(f"Error retrieving AI response: {e}")
            return

        # Display AI response
        if agent_event.data:
          agent_message = agent_event.data["message"]
          st.session_state.messages.append({"role": "assistant", "content": agent_message})
          with st.chat_message("assistant"):
              st.markdown(agent_message)
        else:
          st.error("Error: The response of the AI agent could not be retrieved.")