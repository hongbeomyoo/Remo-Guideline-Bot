import streamlit as st
import requests
import uuid
import time
import random
from bs4 import BeautifulSoup
import os

st.title("REMO GUIDELINE BOT")

# 세션 초기화
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state["history"] = []

api_url = "http://220.82.64.80:6202/chatbot/guideline"

#입력 지연 함수
def display_text_with_delay(container, text, delay):
    output = ""
    for char in text:
        output += char
        container.markdown(
            f"""
            <div class="message-box">{output}</div>
            """,
            unsafe_allow_html=True
        )
        random_delay = random.uniform(delay - 0.01, delay + 0.01)
        time.sleep(max(0, random_delay))
        
# # 스타일 적용 로직
# with open("./style.css") as css:
#     st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)


# 제목 텍스트 디자인
st.markdown("""
    <style>
    h1 {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)
# 스타일 추가
st.markdown(
    """
    <style>
    .message-box {
        background-color: #F7F5EB;
        border-radius: 25px;
        padding: 15px;
        margin: 8px 0;
        color: black;
        display: inline-block;
        min-height: 50px;
        word-wrap: break-word;
        text-indent: 10px; 
    }
    .message-box::after {
        content: "";
        position: absolute;
        left: -7px;
        top: 20px;
        border-width: 10px;
        border-style: solid;
        border-color: #F7F5EB transparent transparent transparent;
    }
    .user-message {
        float: right; 
        text-align: left;
        background-color: #EAE0DA;
        border-radius: 15px;
        padding: 8px 15px;
        margin: 8px 0;
        color: black;
        display: inline-block;
        max-width: 70%;
        word-wrap: break-word; 
        min-height: 10px;
        word-wrap: break-word; 
    }
    .user-message::after {
        content: "";
        position: absolute;
        right: -10px;
        top: 10px;
        border-width: 10px;
        border-style: solid;
        border-color: #EAE0DA transparent transparent transparent;
    }
    .bot-message {
        text-align: left;
        background-color: #dcf8c6;
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
        color: black;
        display: inline-block;
        min-height: 50px; 
        word-wrap: break-word;
    }
    .search-result-box {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 80px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: #EAE0DA;
        word-wrap: break-word;
        word-break: break-all;
        overflow-wrap: break-word;
        display: grid;
        grid-template-rows: auto 1fr auto;
        justify-content: space-between;
        max-width: 100%;
        width: 300px;
        height: 150px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: normal;
    }
    .search-result-box .result-title {
        font-weight: bold;
        font-size: 1.1em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        align-self: start;
    }
    .search-result-box .result-source {
        font-size: 0.9em;
        color: gray;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-top: auto;
        align-self: end;
    }
    .search-result-box a {
        color: black;
        text-decoration: none;
        font-weight: 400;
    }
    .search-result-box a:hover {
        color: gray;
        font-weight: 400;
    }
    .result-title {
        font-size: 18px;
        font-weight: bold;
        color: #0073e6;
        margin-bottom: 8px;
    }
    .result-description {
        font-size: 14px;
        color: #333;
        margin-bottom: 12px;
    }
    .result-source {
        font-size: 12px;
        color: #777;
        text-overflow: ellipsis;
        display: inline-block;
        max-width: 100%;
        overflow: hidden;
        white-space: nowrap;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# # 사용자 입력
# query = st.chat_input(placeholder="질문을 입력하세요.")
# if query :    
#     with st.spinner("답변 생성 중입니다. 잠시만 기다려 주세요..."):
#         # 시스템 프롬프트 미포함
#         response = requests.post(
#             api_url,
#             json={
#                 "session_id": st.session_state["session_id"],
#                 "query": query
#             }
#         )
#         print(response.text)
#     if response.status_code == 200:
#         result = response.json()
#         st.session_state["history"] = result["history"]
#     else:
#         st.error("오류가 발생했습니다. 다시 시도해주세요.")
            
# history = st.session_state["history"]

# # 유저 - 봇 채팅 박스 서로 구분
# for i, message in enumerate(history):
#     if message.startswith("User:"):
#         messagebox = st.empty()
#         messagebox.markdown(
#             f"""
#             <div class="user-message">{message[5:]}</div>
#             """,
#             unsafe_allow_html=True
#         )
#     elif message.startswith("Chatbot:"):
#         if i == len(history) - 1:
#             messagebox = st.empty()
#             display_text_with_delay(messagebox, message[9:], delay=0.02)
#         else:
#             messagebox = st.empty()
#             messagebox.markdown(
#                 f"""
#                 <div class="message-box">{message[9:]}</div>
#                 """,
#                 unsafe_allow_html=True
#             )

query = st.chat_input(placeholder="질문을 입력하세요.")
if query:    
    with st.spinner("답변 생성 중입니다. 잠시만 기다려 주세요..."):
        # 시스템 프롬프트 미포함
        response = requests.post(
            api_url,
            json={
                "session_id": st.session_state["session_id"],
                "query": query
            }
        )
        print(response.text)
    
    if response.status_code == 200:
        result = response.json()
        st.session_state["history"] = result["history"]
    else:
        st.error("오류가 발생했습니다. 다시 시도해주세요.")
            
history = st.session_state["history"]

# 유저 - 봇 채팅 박스 서로 구분
for i, message in enumerate(history):
    if message.startswith("User:"):
        messagebox = st.empty()
        messagebox.markdown(
            f"""
            <div class="user-message">{message[5:]}</div>
            """,
            unsafe_allow_html=True
        )
    
    elif message.startswith("Chatbot:"):
        bot_message = message[9:]  # "Chatbot: " 부분 제거

        # 1️⃣ 로고 요청일 경우 (경로 반환 감지)
        if "회사 로고 파일 경로:" in bot_message:
            logo_path = bot_message.replace("회사 로고 파일 경로:", "").strip()

            # 경로가 올바르면 이미지 표시
            if os.path.exists(logo_path):
                st.image(logo_path, caption="회사 로고", use_container_width=False, width=500)
            else:
                st.warning("로고 파일을 찾을 수 없습니다.")

        # 2️⃣ 일반적인 답변일 경우 (텍스트 출력)
        else:
            if i == len(history) - 1:
                messagebox = st.empty()
                display_text_with_delay(messagebox, bot_message, delay=0.02)
            else:
                messagebox = st.empty()
                messagebox.markdown(
                    f"""
                    <div class="message-box">{bot_message}</div>
                    """,
                    unsafe_allow_html=True
                )