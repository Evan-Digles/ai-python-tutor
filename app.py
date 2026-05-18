import streamlit as st

from tutor.client import TutorAPIError, chat
from tutor.intent import detect
from tutor.modes import MODES
from tutor.tokens import calculate_cost, format_cost, format_tokens

st.set_page_config(
    page_title="Python Tutor",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
if "total_input_tokens" not in st.session_state:
    st.session_state.total_input_tokens = 0
if "total_output_tokens" not in st.session_state:
    st.session_state.total_output_tokens = 0
# [Claude Sonnet 4.6]: two-turn state for exercise grading — "idle" until an exercise is generated
if "exercise_phase" not in st.session_state:
    st.session_state.exercise_phase = "idle"
# [Claude Opus 4.7]: last mode chosen by intent.detect, shown in the header under Auto mode
if "last_detected_mode" not in st.session_state:
    st.session_state.last_detected_mode = ""

# [Claude Opus 4.7]: maps mode keys to the icon + label shown in the sidebar and on each response
MODE_DISPLAY = {
    "explain": "📖 Explain",
    "example": "💻 Example",
    "debug": "🐛 Debug",
    "exercise": "🧩 Exercise",
    "feedback": "💬 Feedback",
}


def _call_api(
    mode_key: str, spinner_text: str = "Thinking...", display_mode: str | None = None
) -> str | None:
    """Call the API for the given mode. Returns response text on success, None on failure."""
    try:
        # [Claude Opus 4.7]: send only role/content — the "mode" key is UI metadata the API rejects
        api_messages = [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]
        with st.spinner(spinner_text):
            response_text, input_tokens, output_tokens = chat(
                system_prompt=MODES[mode_key],
                messages=api_messages,
            )
        st.session_state.total_input_tokens += input_tokens
        st.session_state.total_output_tokens += output_tokens
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text, "mode": display_mode or mode_key}
        )
        return response_text
    except TutorAPIError as e:
        st.error(str(e))
        st.session_state.messages.pop()
        st.session_state.message_count -= 1
        return None


def _handle_exercise() -> None:
    """Two-turn flow: generate an exercise, then grade the student's answer."""
    if st.session_state.exercise_phase == "idle":
        result = _call_api("exercise", "Generating exercise...")
        if result:
            st.session_state.exercise_phase = "awaiting_answer"
            st.rerun()
    else:
        result = _call_api("exercise_grade", "Grading your answer...", display_mode="exercise")
        if result:
            st.session_state.exercise_phase = "idle"
            st.rerun()


# --- Sidebar ---
with st.sidebar:
    st.markdown(
        '<p style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px">Tutor mode</p>',
        unsafe_allow_html=True,
    )
    mode = st.radio(
        "Tutor mode",
        options=["🔀 Auto", *MODE_DISPLAY.values()],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown(
        '<p style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px">Session stats</p>',
        unsafe_allow_html=True,
    )
    total_tokens = st.session_state.total_input_tokens + st.session_state.total_output_tokens
    total_cost = calculate_cost(st.session_state.total_input_tokens, st.session_state.total_output_tokens)
    st.metric("Tokens used", format_tokens(total_tokens))
    st.metric("Est. cost", format_cost(total_cost))
    st.metric("Messages", st.session_state.message_count)

    st.divider()

    if st.button("Clear session"):
        st.session_state.messages = []
        st.session_state.message_count = 0
        st.session_state.total_input_tokens = 0
        st.session_state.total_output_tokens = 0
        st.session_state.exercise_phase = "idle"
        st.session_state.last_detected_mode = ""
        st.rerun()

# --- Main area ---
# [Claude Sonnet 4.6]: strip icon so the mode name maps cleanly to MODES dict keys
mode_label = mode.split(" ", 1)[1]

st.markdown("## 🎓 Python Tutor")
if mode_label == "Auto":
    detected = st.session_state.last_detected_mode
    if detected:
        st.caption(f"Mode: Auto — detected **{detected.capitalize()}** for the last message")
    else:
        st.caption("Mode: Auto — the tutor picks a mode from what you type")
else:
    st.caption(f"Mode: {mode_label}")
st.divider()

if st.session_state.exercise_phase == "awaiting_answer":
    st.info("Exercise generated — type your answer below and submit.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("mode") in MODE_DISPLAY:
            st.caption(MODE_DISPLAY[msg["mode"]])
        st.markdown(msg["content"])

# Dynamic placeholder so the input box reflects the current context
if st.session_state.exercise_phase == "awaiting_answer":
    chat_placeholder = "Type your answer here..."
else:
    chat_placeholder = "Ask your tutor..."

prompt = st.chat_input(chat_placeholder)
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.message_count += 1

    # [Claude Opus 4.7]: a pending exercise answer always routes to exercise mode so
    # the two-turn grading flow can't be broken by intent detection or a mode switch.
    if st.session_state.exercise_phase == "awaiting_answer":
        mode_key = "exercise"
    elif mode_label == "Auto":
        mode_key = detect(prompt)
        st.session_state.last_detected_mode = mode_key
    else:
        mode_key = mode_label.lower()

    if mode_key == "exercise":
        _handle_exercise()
    else:
        result = _call_api(mode_key)
        if result:
            st.rerun()
