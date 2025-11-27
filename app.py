import streamlit as st
import sqlite3
from datetime import datetime

st.set_page_config(page_title="My Channel", layout="wide")

# ----------------- DB 연결 -----------------
conn = sqlite3.connect("channel.db", check_same_thread=False)
c = conn.cursor()

# 채팅 테이블
c.execute("""
CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT,
    message TEXT,
    time TEXT
)
""")

# 게시판 테이블
c.execute("""
CREATE TABLE IF NOT EXISTS board (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    writer TEXT,
    time TEXT
)
""")

# 공지 테이블
c.execute("""
CREATE TABLE IF NOT EXISTS notice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    time TEXT
)
""")

# 관리자 계정 테이블
c.execute("""
CREATE TABLE IF NOT EXISTS admin (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

# 기본 관리자 계정 등록 (없으면 추가)
c.execute("SELECT * FROM admin WHERE username='admin'")
if not c.fetchall():
    c.execute("INSERT INTO admin VALUES (?,?)", ("admin", "1234"))
conn.commit()

# ----------------- 세션 초기화 -----------------
if "admin_login" not in st.session_state:
    st.session_state.admin_login = False

if "admin_username" not in st.session_state:
    st.session_state.admin_username = ""

# ----------------- 사이드바: 관리자 로그인 -----------------
with st.sidebar:
    st.header("🔐 관리자 로그인")
    if not st.session_state.admin_login:
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
            if c.fetchall():
                st.session_state.admin_login = True
                st.session_state.admin_username = username
                st.success(f"관리자로 로그인 됨: {username}")
            else:
                st.error("아이디 또는 비밀번호가 틀림")
    else:
        st.info(f"관리자: {st.session_state.admin_username}")
        if st.button("로그아웃"):
            st.session_state.admin_login = False
            st.session_state.admin_username = ""
            st.success("로그아웃 완료")

# ----------------- 탭 구조 -----------------
tab_home, tab_board, tab_chat = st.tabs(
    ["🏠 홈", "🗂 게시판", "💬 채팅"]
)

# ----------------- 홈 탭: 공지 -----------------
with tab_home:
    st.subheader("📢 공지사항")
    if st.session_state.admin_login:
        n_title = st.text_input("공지 제목", key="n_title")
        n_content = st.text_area("공지 내용", key="n_content")
        if st.button("공지 등록"):
            if n_title and n_content:
                c.execute("INSERT INTO notice VALUES (NULL,?,?,?)",
                          (n_title, n_content, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success("공지 등록 완료")
    notices = c.execute("SELECT title, content, time FROM notice ORDER BY id DESC").fetchall()
    for t, ctt, tm in notices:
        st.markdown(f"### 📌 {t}")
        st.caption(tm)
        st.write(ctt)
        st.write("---")

# ----------------- 게시판 탭 -----------------
with tab_board:
    st.subheader("🗂 팬 게시판")
    title = st.text_input("제목", key="b_title")
    content = st.text_area("내용", key="b_content")
    writer = st.text_input("작성자", key="b_writer")
    if st.button("글쓰기"):
        if title and content and writer:
            c.execute("INSERT INTO board VALUES (NULL,?,?,?,?)",
                      (title, content, writer, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.success("글 등록 완료")
    rows = c.execute("SELECT title, content, writer, time FROM board ORDER BY id DESC").fetchall()
    for t, ctt, w, tm in rows:
        st.markdown(f"### {t}")
        st.caption(f"{w} · {tm}")
        st.write(ctt)
        st.write("---")

# ----------------- 채팅 탭 -----------------
with tab_chat:
    st.subheader("💬 실시간 채팅")
    nick = st.text_input("닉네임", key="chat_nick")
    msg = st.text_input("메시지", key="chat_msg")
    if st.button("전송", key="chat_send"):
        if nick and msg:
            c.execute("INSERT INTO chat VALUES (NULL,?,?,?)",
                      (nick, msg, datetime.now().strftime("%H:%M")))
            conn.commit()
    rows = c.execute("SELECT nickname, message, time FROM chat ORDER BY id DESC LIMIT 50").fetchall()
    for n, m, t in rows[::-1]:
        st.write(f"[{t}] {n}: {m}")

