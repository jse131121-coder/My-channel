import streamlit as st
from datetime import datetime
import sqlite3

st.set_page_config(page_title="My Channel", layout="wide")

# ----------------- DB 연결 -----------------
conn = sqlite3.connect("channel.db", check_same_thread=False)
c = conn.cursor()

# ----------------- 테이블 생성 -----------------
# 프로필
c.execute("""
CREATE TABLE IF NOT EXISTS profile (
    username TEXT PRIMARY KEY,
    bio TEXT,
    profile_url TEXT
)
""")
# 관리자 피드
c.execute("""
CREATE TABLE IF NOT EXISTS feed_admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    image_url TEXT,
    writer TEXT,
    time TEXT
)
""")
# 팬 피드
c.execute("""
CREATE TABLE IF NOT EXISTS feed_fan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    image_url TEXT,
    writer TEXT,
    time TEXT
)
""")
# 채팅
c.execute("""
CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT,
    message TEXT,
    time TEXT
)
""")
# 채팅 테마
c.execute("""
CREATE TABLE IF NOT EXISTS chat_theme (
    id INTEGER PRIMARY KEY,
    bg_color TEXT,
    text_color TEXT
)
""")
conn.commit()

# ----------------- 기본 프로필/테마 -----------------
c.execute("SELECT * FROM profile WHERE username='admin'")
if not c.fetchall():
    c.execute("INSERT INTO profile VALUES (?,?,?)",
              ("admin", "안녕하세요! 프로필 자기소개입니다.", "https://via.placeholder.com/150"))
c.execute("SELECT * FROM chat_theme WHERE id=1")
if not c.fetchall():
    c.execute("INSERT INTO chat_theme VALUES (1, '#FFFFFF', '#000000')")
conn.commit()

# ----------------- 세션 초기화 -----------------
if "show_admin_feed_form" not in st.session_state:
    st.session_state.show_admin_feed_form = False
if "show_fan_feed_form" not in st.session_state:
    st.session_state.show_fan_feed_form = False

# ----------------- 탭 구조 -----------------
tab_profile, tab_home, tab_feed_admin, tab_feed_fan, tab_chat = st.tabs(
    ["👤 프로필", "🏠 홈", "📝 관리자 피드", "📝 팬 피드", "💬 채팅"]
)

# ----------------- 프로필 탭 -----------------
with tab_profile:
    st.subheader("👤 프로필")
    profile = c.execute("SELECT * FROM profile WHERE username='admin'").fetchone()
    st.image(profile[2], width=150)
    st.markdown(f"**{profile[0]}**")
    st.write(profile[1])

# ----------------- 홈 탭 -----------------
with tab_home:
    st.subheader("🏠 링크 모음")
    st.markdown("""
- [유튜브](https://youtube.com)
- [인스타그램](https://instagram.com)
- [팬 카페](https://example.com)
    """)
    st.info("링크를 추가/편집 가능")

# ----------------- 관리자 피드 -----------------
with tab_feed_admin:
    st.subheader("📝 관리자 피드")
    
    # 관리자 게시물 출력
    admin_rows = c.execute("SELECT id, content, image_url, writer, time FROM feed_admin ORDER BY id DESC").fetchall()
    for fid, content, img, writer, tm in admin_rows:
        st.markdown(f"**{writer} · {tm}**")
        st.write(content)
        if img:
            st.image(img, width=300)
        st.write("---")

    # 게시물 추가 버튼
    if st.button("➕ 게시물 추가 (관리자)"):
        st.session_state.show_admin_feed_form = True

    if st.session_state.show_admin_feed_form:
        writer = "admin"
        content = st.text_area("내용", key="admin_content")
        image_url = st.text_input("이미지 URL (선택)", key="admin_img")
        if st.button("게시", key="admin_post"):
            if content:
                c.execute("INSERT INTO feed_admin VALUES (NULL,?,?,?,?)",
                          (content, image_url, writer, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success("게시 완료")
                st.session_state.show_admin_feed_form = False
                st.experimental_rerun()

# ----------------- 팬 피드 -----------------
with tab_feed_fan:
    st.subheader("📝 팬 피드")

    # 팬 게시물 출력
    fan_rows = c.execute("SELECT id, content, image_url, writer, time FROM feed_fan ORDER BY id DESC").fetchall()
    for fid, content, img, writer, tm in fan_rows:
        st.markdown(f"**{writer} · {tm}**")
        st.write(content)
        if img:
            st.image(img, width=300)
        st.write("---")

    # 팬 게시물 작성
    if st.button("➕ 게시물 작성 (팬)"):
        st.session_state.show_fan_feed_form = True

    if st.session_state.show_fan_feed_form:
        writer = st.text_input("작성자 이름", key="fan_writer")
        content = st.text_area("내용", key="fan_content")
        image_url = st.text_input("이미지 URL (선택)", key="fan_img")
        if st.button("게시", key="fan_post"):
            if writer and content:
                c.execute("INSERT INTO feed_fan VALUES (NULL,?,?,?,?)",
                          (content, image_url, writer, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success("게시 완료")
                st.session_state.show_fan_feed_form = False
                st.experimental_rerun()

# ----------------- 채팅 -----------------
with tab_chat:
    st.subheader("💬 오픈 채팅")

    # 관리자 테마 불러오기
    theme = c.execute("SELECT bg_color, text_color FROM chat_theme WHERE id=1").fetchone()
    bg_color, text_color = theme

    # 팬 채팅 표시
    chat_rows = c.execute("SELECT nickname, message, time FROM chat ORDER BY id DESC LIMIT 50").fetchall()
    for n, m, t in chat_rows[::-1]:
        st.markdown(f"<div style='background-color:{bg_color}; color:{text_color}; padding:5px; margin:2px; border-radius:5px;'>[{t}] <b>{n}</b>: {m}</div>", unsafe_allow_html=True)

    # 입력창
    nick = st.text_input("닉네임", key="chat_nick")
    msg = st.text_input("메시지 입력...", key="chat_msg")
    if st.button("전송", key="chat_send"):
        if nick and msg:
            c.execute("INSERT INTO chat VALUES (NULL,?,?,?)",
                      (nick, msg, datetime.now().strftime("%H:%M")))
            conn.commit()
            st.experimental_rerun()

    # 관리자 테마 설정
    st.markdown("---")
    st.subheader("🎨 관리자 채팅 테마 설정")
    new_bg = st.color_picker("배경색", value=bg_color)
    new_text = st.color_picker("글자색", value=text_color)
    if st.button("테마 적용"):
        c.execute("UPDATE chat_theme SET bg_color=?, text_color=? WHERE id=1", (new_bg, new_text))
        conn.commit()
        st.success("채팅 테마 적용 완료")
        st.experimental_rerun()

