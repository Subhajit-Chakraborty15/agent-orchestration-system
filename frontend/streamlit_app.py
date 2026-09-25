import time
import uuid
import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Agent Orchestration System", layout="wide")
st.title("🧠 Agent Orchestration System")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

chat_col, approval_col = st.columns([2, 1])

with chat_col:
    st.subheader("Chat")

    history = requests.get(f"{API_URL}/history/{st.session_state.session_id}").json()
    for turn in history:
        with st.chat_message("user" if turn["role"] == "user" else "assistant"):
            st.write(turn["content"])
            if turn.get("route"):
                st.caption(f"routed to: {turn['route']}")
            if turn.get("needs_approval") and turn.get("approved") is None:
                st.warning("Waiting on human approval before this is finalized.")

    user_input = st.chat_input("Ask the agent system something...")
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)

        resp = requests.post(
            f"{API_URL}/chat",
            json={"session_id": st.session_state.session_id, "message": user_input},
        ).json()
        task_id = resp["task_id"]

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.write("Thinking...")
            for _ in range(60):  # poll up to ~30s
                time.sleep(0.5)
                result = requests.get(f"{API_URL}/chat/{task_id}").json()
                if result["status"] == "done":
                    state = result["result"]
                    if state.get("needs_approval"):
                        placeholder.warning(
                            f"Routed to **{state.get('route')}**. "
                            "Confidence was low, so this is pending human approval "
                            "in the panel on the right."
                        )
                    else:
                        placeholder.write(state.get("final_answer"))
                    break
            else:
                placeholder.write("Still processing — refresh in a moment.")
        st.rerun()

with approval_col:
    st.subheader("⏸️ Pending Approvals")
    pending = requests.get(f"{API_URL}/approvals").json()

    if not pending:
        st.info("Nothing waiting on a human right now.")

    for item in pending:
        with st.container(border=True):
            st.write(f"**Session:** {item['session_id'][:8]}...")
            st.write(f"**Route:** {item['route']}")
            st.write(item["content"])
            edited = st.text_area("Edit answer (optional)", value=item["content"], key=f"edit_{item['id']}")

            c1, c2 = st.columns(2)
            if c1.button("✅ Approve", key=f"approve_{item['id']}"):
                requests.post(
                    f"{API_URL}/approvals/{item['id']}/resolve",
                    json={"approved": True, "edited_answer": edited},
                )
                st.rerun()
            if c2.button("❌ Reject", key=f"reject_{item['id']}"):
                requests.post(
                    f"{API_URL}/approvals/{item['id']}/resolve",
                    json={"approved": False},
                )
                st.rerun()
