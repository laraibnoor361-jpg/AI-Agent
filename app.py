"""
Simple AI Agent - Streamlit + LangChain + Groq
------------------------------------------------
A minimal AI *agent* (not just a chatbot) that can reason about which tool
to use, call it, and use the result to answer the user.
"""

import ast
import operator
from datetime import datetime

import streamlit as st
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_groq import ChatGroq

# ----------------------------
# Tools
# ----------------------------

@tool
def web_search(query: str) -> str:
    """Search the web for current information and return short summaries."""
    from ddgs import DDGS

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))

    if not results:
        return "No results found."

    lines = []
    for r in results:
        lines.append(f"- {r.get('title', '')}: {r.get('body', '')} ({r.get('href', '')})")
    return "\n".join(lines)


# Only these safe math operators are allowed in the calculator tool.
_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _safe_eval(node):
    """Recursively evaluate a math expression's AST, allowing only safe ops."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported or unsafe expression")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic math expression (e.g. '12 * (4 + 3)') and return the result."""
    try:
        tree = ast.parse(expression, mode="eval").body
        result = _safe_eval(tree)
        return f"The result is {result}"
    except Exception as e:
        return f"Could not evaluate '{expression}': {e}"


@tool
def get_current_datetime() -> str:
    """Return today's current date and time."""
    return datetime.now().strftime("%A, %Y-%m-%d %H:%M:%S")


TOOLS = [web_search, calculator, get_current_datetime]

# ----------------------------
# Streamlit page setup
# ----------------------------

st.set_page_config(page_title="Simple AI Agent", page_icon="🤖")
st.title("🤖 Simple AI Agent")
st.caption("A tiny agent with web search, a calculator, and a clock — powered by Groq.")

# Sidebar: API key + clear chat
with st.sidebar:
    st.header("Settings")
    groq_api_key = st.text_input("Groq API key", type="password", help="Get one at console.groq.com")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if not groq_api_key:
    st.warning("Please enter your Groq API key in the sidebar to start chatting.")

# ----------------------------
# Chat history (session state)
# ----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# Chat input + agent call
# ----------------------------

user_input = st.chat_input("Ask me anything...")

if user_input:
    if not groq_api_key:
        st.warning("Please enter your Groq API key in the sidebar first.")
    else:
        # Show and store the user's message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Build the agent (LLM + tools) fresh with the provided key
        with st.chat_message("assistant"):
            try:
                llm = ChatGroq(model="openai/gpt-oss-20b", api_key=groq_api_key)
                agent = create_agent(model=llm, tools=TOOLS)

                result = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
                reply = result["messages"][-1].content

                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Something went wrong: {e}")
