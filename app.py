import streamlit as st
from datetime import datetime
import uuid

st.set_page_config(page_title="Channel", layout="centered")

# ====== 기본 데이터 ======
if "admins" not in st.session_state:
    st.session_state.admins = {
        "admin": "1234",
        "staff": "5678"
    }

if "admin_login" not in st.session_state:
    st.session_state.admin_login = None

if "channel_name" not in st.session_state:
    st.session_state.channel_name = "LINE Channel"

if "bio" not in st.session_state:
    st.session_state.bio = "공식 채널입니다."

if "profile_img" not in st.session_state:
    st.session_state.profile_img = None

if "chapters" not in st.session_state:
    st.session_state.chapters = ["전체"]

if "posts" not in st.session_state:
    st.session_state.posts = []

# ====== 모바일 친화 CSS ======
st.markdown("""
<style>
.post { background:#f7f7f7; padding:16px; border-radius:14px; margin-bottom:16px; }
.title { font-size:17px; font-weight:700; }
.date, .meta { font-size:12px; color:#777; }
button { width:100%; }
</style>
""", unsafe_allow_html=True)

# ====== 관리자 로그인 ======
with st.sidebar:
    st.header("🔐 관리자 로그인")
    admin_id = st.text_input("ID")
    admin_pw = st.text_input("PW", type="password")

    if st.button("로그인"):
        if admin_id in st.session_state.admins and \
           st.session_state.admins[admin_id] == admin_pw:
            st.session_state.admin_login = admin_id
            st.success(f"{admin_id} 로그인 성공")
        else:
            st.error("로그인 실패")

# ====== 관리자 패널 ======
if st.session_state.admin_login:
    with st.sidebar:
        st.header("⚙️ 관리자 설정")

        st.session_state.channel_name = st.text_input(
            "채널 이름", st.session_state.channel_name)
        st.session_state.bio = st.text_area(
            "자기소개", st.session_state.bio)

        img = st.file_uploader("프로필", type=["png","jpg","jpeg"])
        if img:
            st.session_state.profile_img = img

        st.subheader("👤 관리자 추가")
        nid = st.text_input("새 ID")
        npw = st.text_input("새 PW", type="password")
        if st.button("관리자 추가"):
            st.session_state.admins[nid] = npw

        st.subheader("📂 챕터 추가")
        chap = st.text_input("챕터 이름")
        if st.button("추가") and chap:
            st.session_state.chapters.append(chap)

# ====== 프로필 표시 ======
col1, col2 = st.columns([1,3])
with col1:
    st.image(st.session_state.profile_img or "https://via.placeholder.com/80", width=80)
with col2:
    st.markdown(f"### {st.session_state.channel_name}")
    st.caption(st.session_state.bio)

st.write("---")

# ====== 게시물 작성 ======
if st.session_state.admin_login:
    st.subheader("✍️ 게시물 작성")
    title = st.text_input("제목")
    content = st.text_area("내용")
    image = st.file_uploader("사진", type=["png","jpg"])
    chapter = st.selectbox("챕터", st.session_state.chapters)
    pin = st.checkbox("📌 고정")

    if st.button("게시"):
        st.session_state.posts.insert(0,{
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "image": image,
            "chapter": chapter,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "likes": 0,
            "views": 0,
            "comments": [],
            "pinned": pin
        })

# ====== 필터 ======
selected = st.selectbox("📂 분류", st.session_state.chapters)

# ====== 게시물 출력 ======
posts = sorted(st.session_state.posts, key=lambda x:x["pinned"], reverse=True)

for p in posts:
    if selected!="전체" and p["chapter"]!=selected:
        continue

    p["views"] += 1

    st.markdown('<div class="post">', unsafe_allow_html=True)
    st.markdown(f"<div class='title'>{p['title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='meta'>👁 {p['views']} · ❤️ {p['likes']} · {p['time']}</div>", unsafe_allow_html=True)

    if p["image"]:
        st.image(p["image"])
    st.write(p["content"])

    # 좋아요
    if st.button("❤️ 좋아요", key=p["id"]):
        p["likes"] += 1

    # 알림 문구 복사
    copy_text = f"""[{st.session_state.channel_name}]
{p['title']}

{p['content'][:100]}"""

    st.code(copy_text, language=None)

    # 댓글
    st.write("💬 댓글")
    nick = st.text_input("닉네임", key=p["id"]+"n")
    com = st.text_input("댓글 입력", key=p["id"]+"c")
    if st.button("등록", key=p["id"]+"btn"):
        if nick and com:
            p["comments"].append(f"{nick}: {com}")

    for c in p["comments"]:
        st.caption(c)

    st.markdown('</div>', unsafe_allow_html=True)
