import streamlit as st
from graph_manager import PreferenceGraph
from llm_interface import get_response_from_llm
from utils import parse_feedback
import matplotlib.pyplot as plt
import networkx as nx

st.set_page_config(page_title="LLM Preference-Aware System", layout="wide")
st.title("💬 LLM with Personalized Feedback")

# --- User Session ID ---
user_id = st.text_input("Enter your session ID (e.g., name or email):", key="user_id")
if not user_id:
    st.warning("Please enter a session ID to begin.")
    st.stop()

# --- Load Graph for User ---
if 'pg' not in st.session_state or st.session_state.get('current_user') != user_id:
    st.session_state.pg = PreferenceGraph(user_id=user_id)
    st.session_state['current_user'] = user_id

pg = st.session_state.pg

# --- Ask Question ---
question = st.text_input("Ask a question to the AI:")

if question:
    prefs = pg.get_latest_preference()
    response = get_response_from_llm(question, prefs)
    st.markdown("**🤖 Response:**")
    st.write(response)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("👍 Thumbs Up"):
            st.success("Glad you liked it!")
    with col2:
        if st.button("👎 Thumbs Down"):
            st.session_state['show_feedback_box'] = True
            st.session_state['latest_question'] = question

# --- Feedback Box & Updated Response ---
if st.session_state.get("show_feedback_box"):
    feedback = st.text_input("Tell us how to improve (e.g., 'write in bullets, explain in detail')", key="feedback_input")
    if st.button("Submit Feedback"):
        parsed = parse_feedback(feedback)

        for pref in parsed:
            if "don't want" in pref.lower():
                stripped = pref.lower().replace("i don't want", "").strip()
                pg.remove_preference(stripped)
            else:
                pg.add_preference(pref)

        st.success("Preferences updated!")

        # Generate updated response
        latest_prefs = pg.get_latest_preference()
        followup_response = get_response_from_llm(st.session_state['latest_question'], latest_prefs)
        st.markdown("**🤖 Updated Response:**")
        st.write(followup_response)

        st.session_state['show_feedback_box'] = False

# --- Visualize Graph ---
st.subheader("🧠 User Preference Graph")

def plot_graph(G):
    pos = nx.spring_layout(G, seed=42)
    edge_colors = [d.get('color', 'gray') for _, _, d in G.edges(data=True)]
    labels = {}
    for u, v, attr in G.edges(data=True):
        label = attr.get('color', '')
        if label == 'black':
            labels[(u, v)] = '❌'
        else:
            labels[(u, v)] = label

    plt.figure(figsize=(12, 6))
    nx.draw(G, pos, with_labels=True, node_color="skyblue", edge_color=edge_colors,
            node_size=2400, font_size=10, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color='red',
                                 font_size=10, bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2'))
    st.pyplot(plt)

plot_graph(pg.get_graph())

# --- Reset Button ---
st.subheader("🧹 Reset System")

if st.button("Reset Memory"):
    pg.reset()
    st.success("Memory has been reset. Please reload or ask a new question.")
    st.session_state['show_feedback_box'] = False
