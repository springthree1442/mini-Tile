import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo


# =========================
# 1. 기본 설정
# =========================

st.set_page_config(
    page_title="Mini Tile",
    page_icon="🎈",
    layout="centered"
)

st.title("🎈 Mini Tile")
st.caption("X 끊으려고 만든 자체 디지털 쓰레기통")


# =========================
# 2. 데이터베이스 연결
# =========================

def get_connection():
    return sqlite3.connect("mini_x.db", check_same_thread=False)


conn = get_connection()
cursor = conn.cursor()


# =========================
# 3. 테이블 만들기
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
)
""")

conn.commit()


# =========================
# 4. 비밀번호 암호화 함수
# =========================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# 5. 회원가입 함수
# =========================

def signup(username, password):
    hashed_pw = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_pw)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


# =========================
# 6. 로그인 확인 함수
# =========================

def login(username, password):
    hashed_pw = hash_password(password)

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hashed_pw)
    )

    user = cursor.fetchone()
    return user is not None


# =========================
# 7. 게시글 저장 함수
# =========================

def add_post(username, content):
    created_at = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO posts (username, content, created_at) VALUES (?, ?, ?)",
        (username, content, created_at)
    )
    conn.commit()


# =========================
# 8. 게시글 불러오기 함수
# =========================

def get_posts():
    cursor.execute(
        "SELECT username, content, created_at FROM posts ORDER BY id DESC"
    )
    return cursor.fetchall()


# =========================
# 9. 로그인 상태 저장
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# =========================
# 10. 사이드바 메뉴
# =========================

menu = st.sidebar.radio(
    "메뉴",
    ["홈", "회원가입", "로그인"]
)


# =========================
# 11. 회원가입 화면
# =========================

if menu == "회원가입":
    st.subheader("회원가입")

    new_username = st.text_input("아이디")
    new_password = st.text_input("비밀번호", type="password")
    new_password_check = st.text_input("비밀번호 확인", type="password")

    if st.button("회원가입하기"):
        if not new_username or not new_password:
            st.warning("아이디와 비밀번호를 입력해주세요.")

        elif new_password != new_password_check:
            st.warning("비밀번호가 서로 다릅니다.")

        else:
            result = signup(new_username, new_password)

            if result:
                st.success("회원가입이 완료되었습니다. 이제 로그인해주세요.")
            else:
                st.error("이미 존재하는 아이디입니다.")


# =========================
# 12. 로그인 화면
# =========================

elif menu == "로그인":
    st.subheader("로그인")

    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인하기"):
        if login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"{username}님, 로그인되었습니다.")
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")


# =========================
# 13. 홈 화면
# =========================

elif menu == "홈":
    if st.session_state.logged_in:
        st.success(f"현재 로그인한 사용자: {st.session_state.username}")

        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

        st.divider()

        st.subheader("게시글 작성")

        content = st.text_area(
            "무슨 일이 있었나요?",
            max_chars=200
        )

        if st.button("게시하기"):
            if content.strip():
                add_post(st.session_state.username, content)
                st.success("게시글이 등록되었습니다.")
                st.rerun()
            else:
                st.warning("내용을 입력해주세요.")

    else:
        st.info("글을 작성하려면 먼저 로그인해주세요.")

    st.divider()

    st.subheader("게시글 목록")

    posts = get_posts()

    if posts:
        for post in posts:
            username, content, created_at = post

            st.markdown(f"### @{username}")
            st.markdown(content.replace("\n", "<br>"), unsafe_allow_html=True)
            st.caption(created_at)
            st.divider()
    else:
        st.write("아직 게시글이 없습니다.")
