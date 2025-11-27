import streamlit as st
from datetime import datetime
import json
import os
import base64

st.set_page_config(page_title="My Channel Chat", layout="wide")

DATA_FILE = "channel_data.json"

# ----------------- JSON 초기화 -----------------
if not os.path.exists(DATA_FILE):
    data = {
        "chat": [],
        "chat_theme": {
            "bg_color": "#DCF8C6",  # 카톡 기본 배경색
            "user_color": "#FFFFFF",  # 팬/친구 메시지
            "admin_color": "#E1F0FF",  # 관리자 답변
            "text_color": "#000000"
        }
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
else:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

# ----------------- 세션 초기화 -----------------
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "chat_nick" not in st.session_state:
    st.session_state.chat_nick = ""
if "chat_msg" not in st.session_state:
    st.session_state.chat_msg = ""

# ----------------- 사이드바 로그인 -----------------
st.sidebar.subheader("관리자 로그인")
if not st.session_state.admin_logged_in:
    username = st.sidebar.text_input("아이디")
    password = st.sidebar.text_input("비밀번호", type="password")
    if st.sidebar.button("로그인"):
        if username == "admin" and password == "1234":  # 간단 샘플
            st.session_state.admin_logged_in = True
            st.sidebar.success("관리자 로그인 성공")
            st.rerun()
        else:
            st.sidebar.error("아이디 또는 비밀번호 틀림")
else:
    st.sidebar.success("관리자 로그인 상태 ✅")
    if st.sidebar.button("로그아웃"):
        st.session_state.admin_logged_in = False
        st.rerun()

# ----------------- 채팅 탭 -----------------
st.title("💬 팬/관리자 채팅")

theme = data["chat_theme"]
bg_color = theme["bg_color"]
user_color = theme["user_color"]
admin_color = theme["admin_color"]
text_color = theme["text_color"]

# ----------------- 채팅 표시 -----------------
st.subheader("채팅 창 (최신 메시지 위로)")

for chat in reversed(data["chat"][-100:]):  # 최대 100개 메시지 표시
    if chat.get("is_admin"):
        color = admin_color
        sender = "관리자"
    else:
        color = user_color
        sender = chat.get("nickname", "팬")
    st.markdown(
        f"<div style='background-color:{color}; color:{text_color}; padding:8px; margin:4px; border-radius:10px; max-width:70%; float:left; clear:both;'>"
        f"<b>{sender}</b> [{chat['time']}]: {chat['message']}</div><div style='clear:both;'></div>",
        unsafe_allow_html=True
    )

# ----------------- 메시지 입력 -----------------
st.subheader("메시지 작성")

if not st.session_state.admin_logged_in:
    st.session_state.chat_nick = st.text_input("닉네임", value=st.session_state.chat_nick)
msg_input = st.text_input("메시지 입력...", value=st.session_state.chat_msg)

if st.button("전송"):
    if st.session_state.admin_logged_in:
        # 관리자 메시지
        if msg_input.strip():
            data["chat"].append({
                "nickname": "관리자",
                "message": msg_input.strip(),
                "time": datetime.now().strftime("%H:%M"),
                "is_admin": True
            })
            st.session_state.chat_msg = ""
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            st.rerun()
    else:
        # 팬/친구 메시지
        if msg_input.strip() and st.session_state.chat_nick.strip():
            data["chat"].append({
                "nickname": st.session_state.chat_nick.strip(),
                "message": msg_input.strip(),
                "time": datetime.now().strftime("%H:%M"),
                "is_admin": False
            })
            st.session_state.chat_msg = ""
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            st.rerun()

# ----------------- 관리자 테마 변경 -----------------
if st.session_state.admin_logged_in:
    st.markdown("---")
    st.subheader("🎨 채팅 테마 변경 (관리자)")
    new_bg = st.color_picker("전체 배경색", value=bg_color)
    new_user = st.color_picker("팬 메시지 배경색", value=user_color)
    new_admin = st.color_picker("관리자 메시지 배경색", value=admin_color)
    new_text = st.color_picker("글자색", value=text_color)

    if st.button("테마 적용"):
        data["chat_theme"]["bg_color"] = new_bg
        data["chat_theme"]["user_color"] = new_user
        data["chat_theme"]["admin_color"] = new_admin
        data["chat_theme"]["text_color"] = new_text
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        st.success("채팅 테마 적용 완료")
        st.rerun()

