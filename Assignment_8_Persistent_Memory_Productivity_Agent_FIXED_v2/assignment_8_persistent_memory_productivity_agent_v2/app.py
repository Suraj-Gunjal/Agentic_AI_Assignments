import streamlit as st

from src.agent import ProductivityMemoryAgent


st.set_page_config(
    page_title="Persistent Memory Agent",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Persistent Memory Productivity Agent")
st.caption("LangGraph + ChromaDB + Ollama")

st.write(
    "A local student assistant that extracts useful long-term information, "
    "stores it persistently, retrieves relevant memories, and uses them "
    "to answer future questions."
)


@st.cache_resource
def get_agent():
    return ProductivityMemoryAgent()


agent = get_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("🧠 Persistent Memory")

    memories = agent.memory.all_records()
    st.metric("Stored memories", len(memories))

    st.divider()

    st.write("### Example memories")
    st.code(
        """I prefer studying DSA in the morning.
I am building a flood prediction project.
My goal is to improve Java problem solving.
I prefer simple project documentation.""",
        language="text",
    )

    st.write("### Try asking")
    st.code(
        """What do you remember about my study preferences?
What should I work on in the morning?
What project am I building?
What am I trying to improve?""",
        language="text",
    )

    st.divider()

    if st.button("Clear all memories", use_container_width=True):
        agent.memory.clear()
        st.session_state.messages = []
        st.success("All memories cleared.")
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_message = st.chat_input(
    "Tell me something or ask about your memories..."
)

if user_message:
    st.session_state.messages.append(
        {"role": "user", "content": user_message}
    )

    with st.chat_message("user"):
        st.write(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Processing memory and generating answer..."):
            result = agent.chat(user_message)

        st.write(result["answer"])

        if result.get("memory_stored"):
            st.caption("🧠 A useful long-term memory was stored.")
        elif result.get("should_store") and result.get("candidate_memory"):
            st.caption("ℹ️ This information was already in memory.")

    st.session_state.messages.append(
        {"role": "assistant", "content": result["answer"]}
    )

st.divider()

st.subheader("📚 Stored Long-Term Memories")

memories = agent.memory.all_records()

if memories:
    for i, record in enumerate(memories, start=1):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(f"**{i}.** {record['memory']}")
        with col2:
            st.caption(record["category"])
else:
    st.info("No memories stored yet.")
