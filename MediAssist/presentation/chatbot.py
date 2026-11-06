
"""Chat interface for MediAssist AI."""

import streamlit as st

from rag.rag_chain import RAGChain


FALLBACK_ANSWER = (
    "I’m sorry, but I couldn’t find sufficient information in the "
    "available documents to answer your question accurately. "
    "Please upload a relevant document or provide additional context "
    "so I can assist you."
)


@st.cache_resource
def get_rag_chain():
    """Create and reuse the RAG chain for the current Streamlit server."""
    return RAGChain()


def render_chatbot():
    """Render the MediAssist AI chatbot and conversation history."""

    st.subheader("MediAssist AI Chatbot")
    st.caption(
        "Ask questions about your uploaded healthcare documents. "
        "Answers are generated using the available document context."
    )

    # Initialize conversation history once per user session.
    if "mediassist_chat_history" not in st.session_state:
        st.session_state.mediassist_chat_history = []

    # Display older conversations first and newer conversations last.
    for message in st.session_state.mediassist_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show sources below assistant answers when available.
            if message["role"] == "assistant" and message.get("sources"):
                with st.expander("View source documents"):
                    for index, source in enumerate(
                        message["sources"], start=1
                    ):
                        source_name = source.get(
                            "source", "Unknown source"
                        )
                        page = source.get("page")

                        st.markdown(f"**Source {index}: {source_name}**")

                        if page is not None:
                            st.caption(f"Page: {page}")

                        content = source.get("content", "")
                        if content:
                            st.text(
                                content[:1500]
                                + ("..." if len(content) > 1500 else "")
                            )

    # Chat input appears at the bottom of the conversation.
    question = st.chat_input(
        "Ask a question about your uploaded documents..."
    )

    if question and question.strip():
        question = question.strip()

        # Display the submitted question immediately.
        with st.chat_message("user"):
            st.markdown(question)

        try:
            with st.chat_message("assistant"):
                with st.spinner("Searching documents and preparing an answer..."):
                    rag_chain = get_rag_chain()
                    result = rag_chain.ask(question)

                answer = str(result.get("answer", "")).strip()
                sources = result.get("sources", [])

                # Convert the RAG chain's fallback to the requested message.
                if (
                    not answer
                    or answer.strip().upper() == "I DON'T KNOW"
                    or answer.strip().upper() == "I DONT KNOW"
                ):
                    answer = FALLBACK_ANSWER
                    sources = []

                st.markdown(answer)

                if sources:
                    with st.expander("View source documents"):
                        for index, source in enumerate(sources, start=1):
                            source_name = source.get(
                                "source", "Unknown source"
                            )
                            page = source.get("page")

                            st.markdown(
                                f"**Source {index}: {source_name}**"
                            )

                            if page is not None:
                                st.caption(f"Page: {page}")

                            content = source.get("content", "")
                            if content:
                                st.text(
                                    content[:1500]
                                    + ("..." if len(content) > 1500 else "")
                                )

            # Store the conversation in FIFO order.
            st.session_state.mediassist_chat_history.append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            st.session_state.mediassist_chat_history.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                }
            )

            # Refresh so the saved conversation appears in order.
            st.rerun()

        except Exception as exc:
            st.error(
                "Unable to process your question right now. "
                "Please check the RAG configuration and try again."
            )
            # Keep technical details in the server logs.
            print(f"MediAssist chatbot error: {exc}")


def main():
    """Allow the chatbot to run independently for testing."""
    st.set_page_config(
        page_title="MediAssist AI Chatbot",
        page_icon="🏥",
        layout="wide",
    )
    render_chatbot()


if __name__ == "__main__":
    main()
