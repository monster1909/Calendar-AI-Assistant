import streamlit as st
import os
import json
from datetime import datetime
import pytz

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Calendar AI Assistant",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Be Vietnam Pro', sans-serif;
}

.stApp {
    background: #0f1117;
    color: #e8eaf0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #161b27;
    border-right: 1px solid #2a2f3f;
}

/* Chat message - user */
.user-msg {
    background: linear-gradient(135deg, #1e3a5f, #1a3050);
    border: 1px solid #2a4a70;
    border-radius: 12px 12px 4px 12px;
    padding: 12px 16px;
    margin: 8px 0;
    margin-left: 20%;
    font-size: 0.95rem;
    line-height: 1.6;
}

/* Chat message - assistant */
.assistant-msg {
    background: linear-gradient(135deg, #1a1f2e, #1e2338);
    border: 1px solid #2a3050;
    border-radius: 12px 12px 12px 4px;
    padding: 12px 16px;
    margin: 8px 0;
    margin-right: 20%;
    font-size: 0.95rem;
    line-height: 1.6;
}

/* Event card */
.event-card {
    background: #1a2035;
    border: 1px solid #2a3560;
    border-left: 4px solid #4a9eff;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    font-family: 'Be Vietnam Pro', sans-serif;
}
.event-card .event-title {
    font-weight: 600;
    color: #7ab8ff;
    font-size: 1rem;
}
.event-card .event-meta {
    color: #8892a4;
    font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 4px;
}

/* Tool badge */
.tool-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 8px;
}
.badge-create  { background: #1a4a2a; color: #4ade80; border: 1px solid #2a6a3a; }
.badge-delete  { background: #4a1a1a; color: #f87171; border: 1px solid #6a2a2a; }
.badge-search  { background: #1a3a4a; color: #60c8ff; border: 1px solid #2a5a6a; }
.badge-display { background: #3a3a1a; color: #facc15; border: 1px solid #5a5a2a; }
.badge-none    { background: #2a2a2a; color: #9ca3af; border: 1px solid #3a3a3a; }

/* Input area */
.stTextInput input {
    background: #1a1f2e !important;
    border: 1px solid #2a3050 !important;
    color: #e8eaf0 !important;
    border-radius: 8px !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
}
.stTextInput input:focus {
    border-color: #4a9eff !important;
    box-shadow: 0 0 0 2px rgba(74,158,255,0.15) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1e4a8a, #1a3a7a);
    color: #e8eaf0;
    border: 1px solid #2a5a9a;
    border-radius: 8px;
    font-family: 'Be Vietnam Pro', sans-serif;
    font-weight: 500;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2a5a9a, #234a8a);
    border-color: #4a9eff;
    transform: translateY(-1px);
}

/* Header */
.page-header {
    text-align: center;
    padding: 20px 0 10px;
}
.page-header h1 {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #4a9eff, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.page-header p {
    color: #6b7280;
    font-size: 0.9rem;
    margin-top: 4px;
}

/* Status indicator */
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}
.status-ok  { background: #4ade80; box-shadow: 0 0 6px #4ade80; }
.status-err { background: #f87171; box-shadow: 0 0 6px #f87171; }

/* Log box */
.log-box {
    background: #0d1117;
    border: 1px solid #2a2f3f;
    border-radius: 8px;
    padding: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #6b7280;
    max-height: 200px;
    overflow-y: auto;
}

/* Divider */
hr { border-color: #2a2f3f !important; }

/* Streamlit overrides */
[data-testid="stMarkdownContainer"] p { color: #c8ccd8; }
.stSelectbox label, .stSlider label { color: #8892a4 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Load core module with error handling
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_calendar_module():
    """Import the calendar module once; cache the result."""
    try:
        import calendar_agent as ca  # rename your file to calendar_agent.py
        return ca, None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────
# Helper: format events as HTML cards
# ─────────────────────────────────────────────
def render_event_cards(events: list) -> str:
    if not events:
        return "<p style='color:#6b7280;font-size:0.9rem;'>Không tìm thấy sự kiện nào.</p>"

    local_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    from dateutil import parser as dparser

    html = ""
    for ev in events:
        try:
            s = dparser.isoparse(ev["start"]["dateTime"]).astimezone(local_tz)
            e = dparser.isoparse(ev["end"]["dateTime"]).astimezone(local_tz)
            start_str = s.strftime("%d/%m/%Y %H:%M")
            end_str   = e.strftime("%H:%M")
        except Exception:
            start_str = end_str = "N/A"

        title    = ev.get("summary", "[Không có tiêu đề]")
        location = ev.get("location", "")
        desc     = ev.get("description", "")
        ev_id    = ev.get("id", "")[:12] + "…"

        loc_line  = f"<br>📍 {location}" if location else ""
        desc_line = f"<br>📝 {desc}"     if desc else ""

        html += f"""
        <div class="event-card">
            <div class="event-title">📅 {title}</div>
            <div class="event-meta">
                🕐 {start_str} – {end_str}{loc_line}{desc_line}<br>
                🔑 ID: <code>{ev_id}</code>
            </div>
        </div>"""
    return html


# ─────────────────────────────────────────────
# Tool badge map
# ─────────────────────────────────────────────
TOOL_LABEL = {
    1: ("create",  "➕ Tạo sự kiện"),
    2: ("delete",  "🗑️ Xóa toàn bộ"),
    3: ("delete",  "🗑️ Xóa theo tiêu đề"),
    4: ("display", "📋 Hiển thị lịch"),
    5: ("search",  "🔍 Tìm kiếm"),
    6: ("none",    "❓ Không xác định"),
}


# ─────────────────────────────────────────────
# Session state init
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logs" not in st.session_state:
    st.session_state.logs = []


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Cấu hình")
    st.divider()

    # API Key input (fallback if not in .env)
    anthropic_key = st.text_input(
        "Anthropic API Key",
        value=os.getenv("anthropic_api_key", ""),
        type="password",
        help="Sẽ dùng .env nếu để trống",
    )
    if anthropic_key:
        os.environ["anthropic_api_key"] = anthropic_key

    st.divider()

    # Calendar connection status
    ca, err = load_calendar_module()
    if ca:
        st.markdown('<span class="status-dot status-ok"></span>**Google Calendar**: Kết nối OK', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-dot status-err"></span>**Google Calendar**: Lỗi', unsafe_allow_html=True)
        st.caption(f"```{err}```")

    st.divider()

    st.markdown("### 📌 Lệnh mẫu")
    examples = [
        "Tạo lịch họp team chiều mai lúc 14h tới 16h",
        "Tuần này có lịch gì không?",
        "Tìm lịch họp trong tuần tới",
        "Xóa tất cả sự kiện ngày mai",
        "Xóa lịch học máy học tuần này",
        "Sáng thứ hai tuần sau có gì?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True, key=f"ex_{ex[:20]}"):
            st.session_state["pending_input"] = ex

    st.divider()
    if st.button("🧹 Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.logs = []
        st.rerun()

    # Show logs
    if st.session_state.logs:
        st.markdown("### 🪵 Debug Log")
        log_html = "<div class='log-box'>" + "<br>".join(st.session_state.logs[-50:]) + "</div>"
        st.markdown(log_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Main area
# ─────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>🗓️ Calendar AI Assistant</h1>
    <p>Quản lý Google Calendar bằng tiếng Việt tự nhiên</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Chat history
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        html_class = "user-msg" if role == "user" else "assistant-msg"
        prefix = "🧑" if role == "user" else "🤖"
        st.markdown(
            f'<div class="{html_class}">{prefix} {content}</div>',
            unsafe_allow_html=True,
        )

st.divider()

# ─────────────────────────────────────────────
# Input
# ─────────────────────────────────────────────
pending = st.session_state.pop("pending_input", None)

with st.form("chat_form", clear_on_submit=True):
    cols = st.columns([9, 1])
    with cols[0]:
        user_input = st.text_input(
            "Nhập lệnh",
            value=pending or "",
            placeholder='Ví dụ: "Tạo lịch họp sáng mai lúc 9h tới 11h"',
            label_visibility="collapsed",
        )
    with cols[1]:
        submitted = st.form_submit_button("Gửi", use_container_width=True)


# ─────────────────────────────────────────────
# Process
# ─────────────────────────────────────────────
if submitted and user_input.strip():
    prompt = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": prompt})

    if ca is None:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ Không thể kết nối module: {err}",
        })
        st.rerun()

    with st.spinner("⏳ Đang xử lý..."):
        try:
            # 1. Determine action
            tool_info = ca.switch_task(prompt)
            tool_number = tool_info.get("tool_number", 6)
            badge_cls, badge_label = TOOL_LABEL.get(tool_number, ("none", "❓"))

            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] tool={tool_number} | prompt={prompt[:60]}"
            st.session_state.logs.append(log_entry)

            badge_html = f'<span class="tool-badge badge-{badge_cls}">{badge_label}</span>'

            # 2. Dispatch
            reply_html = badge_html + "<br>"

            if tool_number == 1:
                summary, start, end, location, description = ca.format_prompt_to_create(prompt)
                if start and end:
                    ca.create_event(summary, start, end, location or "", description or "")
                    reply_html += (
                        f"✅ Đã tạo sự kiện <b>{summary}</b><br>"
                        f"<span style='color:#8892a4;font-size:0.85rem;font-family:monospace'>"
                        f"⏰ {start} → {end}"
                        + (f"<br>📍 {location}" if location else "")
                        + (f"<br>📝 {description}" if description else "")
                        + "</span>"
                    )
                else:
                    reply_html += "⚠️ Không thể xác định thời gian. Vui lòng nói rõ hơn."

            elif tool_number == 2:
                events, _ = ca.handle_time_and_events(prompt)
                if events:
                    ca.delete_events(events)
                    reply_html += f"🗑️ Đã xóa <b>{len(events)}</b> sự kiện."
                else:
                    reply_html += "ℹ️ Không tìm thấy sự kiện nào trong khoảng thời gian này."

            elif tool_number == 3:
                events, title = ca.handle_time_and_events(prompt)
                if title:
                    events = ca.search_event_by_title(events, title, threshold=0.6)
                if events:
                    ca.delete_events(events)
                    reply_html += f"🗑️ Đã xóa <b>{len(events)}</b> sự kiện khớp với «{title}»."
                else:
                    reply_html += f"ℹ️ Không tìm thấy sự kiện nào khớp với «{title}»."

            elif tool_number == 4:
                events, _ = ca.handle_time_and_events(prompt)
                reply_html += f"📋 Tìm thấy <b>{len(events)}</b> sự kiện:<br>"
                reply_html += render_event_cards(events)

            elif tool_number == 5:
                events, title = ca.handle_time_and_events(prompt)
                if title:
                    events = ca.search_event_by_title(events, title, threshold=0.6)
                reply_html += f"🔍 Tìm thấy <b>{len(events)}</b> kết quả cho «{title}»:<br>"
                reply_html += render_event_cards(events)

            else:
                reply_html += "🤔 Mình chưa hiểu yêu cầu này. Thử lại với cú pháp khác nhé!"

        except Exception as exc:
            import traceback
            tb = traceback.format_exc()
            st.session_state.logs.append(f"[ERROR] {tb[:300]}")
            reply_html = f"❌ Lỗi xử lý: <code>{str(exc)}</code>"

    st.session_state.messages.append({"role": "assistant", "content": reply_html})
    st.rerun()