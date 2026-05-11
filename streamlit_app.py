import streamlit as st
import uuid
import os
from pathlib import Path
from langgraph_agent_lab.graph import build_graph
from langgraph_agent_lab.persistence import build_checkpointer
from langgraph_agent_lab.state import Scenario, Route, initial_state

st.set_page_config(
    page_title="LangGraph Support Agent",
    page_icon="🤖",
    layout="centered",
)

# Header with beautiful styling
st.title("🤖 LangGraph Support Center")
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("🔧 Config & History")
    
    # Enable true HITL via env override for the duration of this run
    use_hitl = st.toggle("Enable HITL mode (Manual Approval Required)", value=True)
    if use_hitl:
        os.environ["LANGGRAPH_INTERRUPT"] = "true"
    else:
        os.environ["LANGGRAPH_INTERRUPT"] = "false"

    session_id = st.text_input("Active Session Thread ID", value=st.session_state.get("active_thread", str(uuid.uuid4())[:8]))
    st.session_state["active_thread"] = session_id

    # Initialize the graph pipeline
    # Use local sqlite persistence mapped relative to app cwd
    db_path = os.path.join(os.getcwd(), "lab.db")
    checkpointer = build_checkpointer("sqlite", db_path)
    graph = build_graph(checkpointer=checkpointer)
    
    st.success("✅ Graph Ready")
    
    # Mermaid visualize block
    with st.expander("Show Architecture (Mermaid)"):
        try:
            mermaid_png = graph.get_graph().draw_mermaid_png()
            st.image(mermaid_png)
        except Exception:
            mermaid_txt = graph.get_graph().draw_mermaid()
            st.code(mermaid_txt)

config = {"configurable": {"thread_id": session_id}}

# Fetch current snapshot to determine if system is paused at an interrupt
snapshot = graph.get_state(config)

# Display workflow summary state
st.subheader("🗨 Interaction")

# Handle active interrupt state before standard UI flow
if snapshot.next and "approval" in snapshot.next:
    st.warning("⚠️ SYSTEM PAUSED: High-risk action requires explicit confirmation.")
    
    task_description = snapshot.values.get("proposed_action", "No details")
    st.info(f"**Requested Action:** {task_description}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ APPROVE", use_container_width=True):
            graph.update_state(config, {"approval": {"approved": True, "comment": "Approved via UI"}}, as_node="approval")
            graph.invoke(None, config=config)
            st.rerun()
    with col2:
        if st.button("❌ REJECT", type="primary", use_container_width=True):
            graph.update_state(config, {"approval": {"approved": False, "comment": "Rejected via UI"}}, as_node="approval")
            graph.invoke(None, config=config)
            st.rerun()

# Display conversation history from current snapshot if not finished
if snapshot.values:
    st.markdown("### Current State Data")
    col1, col2 = st.columns(2)
    col1.metric("Current Route", str(snapshot.values.get('route', 'N/A')))
    col2.metric("Attempts", str(snapshot.values.get('attempt', 0)))
    
    if snapshot.values.get("final_answer"):
        st.success(f"**Agent:** {snapshot.values.get('final_answer')}")
    
    with st.expander("Diagnostic Trace Details"):
        st.json({
            "latency_log": snapshot.values.get("latency_log", []),
            "events": snapshot.values.get("events", [])
        })

st.markdown("---")

# Message Composer
user_input = st.chat_input("Explain your problem...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    
    # Boot execution
    scen = Scenario(id=session_id, query=user_input, expected_route=Route.SIMPLE)
    init_state = initial_state(scen)
    
    with st.spinner("Thinking..."):
        result = graph.invoke(init_state, config=config)
    
    st.rerun()
