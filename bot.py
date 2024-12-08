from fpdf import FPDF
import streamlit as st
import openai
import PyPDF2
from datetime import datetime
import base64
st.set_page_config(page_title="Super Chat bot", layout="wide")
def add_bg_from_url():
    with open("image.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url('data:image/png;base64,{encoded_string}');
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center center;
        }}
        h3 {{
            color: #87CEEB;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
add_bg_from_url()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "reactions" not in st.session_state:
    st.session_state.reactions = {} 
with st.sidebar:
    st.title("⚙️ Sozlamalar")
    api_key = st.text_input("OpenAI API kalitini kiriting:", type="password", placeholder="API kalitini kiriting...")
    uploaded_file = st.file_uploader("PDF faylini yuklang:", type=["pdf"])
    if st.button("Tasdiqlash"):
        if not api_key or not uploaded_file:
            st.error("Iltimos, API kalitini va PDF faylni yuklang!")
        else:
            st.success("Sozlamalar muvaffaqiyatli tasdiqlandi!")
            st.session_state.api_key = api_key
            st.session_state.uploaded_file = uploaded_file

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"PDF matnini o'qishda xatolik: {e}")
        return ""

if "api_key" in st.session_state and "uploaded_file" in st.session_state:
    openai.api_key = st.session_state.api_key

    if "pdf_text" not in st.session_state:
        pdf_text = extract_text_from_pdf(st.session_state.uploaded_file)
        st.session_state.pdf_text = pdf_text

    st.title("Super chat bot 🤖")
    st.write("Fayldan olingan ma'lumotlar asosida savollaringizga javob beraman.")

    chat_history_container = st.container()
    with chat_history_container:
        st.markdown("<h3>💬🗺️ Chat xabarlari</h3>", unsafe_allow_html=True)
        for i, chat in enumerate(st.session_state.chat_history):
            if i % 2 == 0:  
                user_message = f"""
                <div style='
                    padding: 10px 15px; 
                    margin-bottom: 10px; 
                    border-radius: 10px; 
                    background-color: #90EE90; 
                    color: black; 
                    width: fit-content;
                    max-width: 70%;
                    margin-left: auto;
                '>
                    {chat['content']} <br>
                    <small style='color: gray;'> {chat['time']} </small>
                </div>
                """
                st.markdown(user_message, unsafe_allow_html=True)
            else:  
                bot_message = f"""
                <div style='
                    padding: 10px 15px; 
                    margin-bottom: 10px; 
                    border-radius: 10px; 
                    background-color: #ADD8E6; 
                    color: black; 
                    width: fit-content;
                    max-width: 70%;
                '>
                    {chat['content']} <br>
                    <small style='color: gray;'> {chat['time']} </small>
                </div>
                """
                st.markdown(bot_message, unsafe_allow_html=True)

                if i not in st.session_state.reactions:
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("👍🏽", key=f"like_{i}"):
                            st.session_state.reactions[i] = "👍🏽"
                            st.experimental_rerun()
                    with col2:
                        if st.button("👎🏽", key=f"dislike_{i}"):
                            st.session_state.reactions[i] = "👎🏽"
                            st.experimental_rerun()
                else:
                    reaction = st.session_state.reactions[i]
                    if st.button(f"{reaction}", key=f"reaction_{i}"):
                        del st.session_state.reactions[i]
                        st.experimental_rerun()

    user_input_container = st.container()
    with user_input_container:
        st.markdown("<h3>Savolingizni yozing:</h3>", unsafe_allow_html=True)
        if "user_input" not in st.session_state:
            st.session_state.user_input = ""  
        user_input = st.text_input(
            "",
            placeholder="Savolingizni kiriting...",
            value=st.session_state.user_input,
            key="user_input_key",
        )

        if st.button("Yuborish", key="send"):
            if user_input.strip():
                current_time = datetime.now().strftime("%H:%M:%S")
                prompt = f"""
                Sizga PDF fayldan olingan quyidagi ma'lumotlar taqdim etiladi:
                {st.session_state.pdf_text}
                Foydalanuvchi quyidagi savolni berdi:
                "{user_input}"
                Javobingizni iloji boricha qisqa va aniq qiling. Agar savolga javobni matndan topa olmasangiz:
                Agar u sizdan sizning kim ekanligingizni so'rasa unga "Men berilgan ma'lumotlar orqali sizning savollaringizga javob beradigan botman" deb javoob qaytaring.
                Agar u shunga o'xshash savollarni bersa ham shunaqa javob bering boshqa holatlarda "Menda ma'lumot yetarli emas, men bu savolga javo bera olmayman" deb javob qaytaring.
                """
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                    )
                    bot_response = response['choices'][0]['message']['content']

                    st.session_state.chat_history.extend([
                        {"content": user_input, "time": current_time},
                        {"content": bot_response, "time": current_time},
                    ])
                    st.session_state.user_input = ""  
                    st.experimental_rerun()

                except Exception as e:
                    st.error(f"OpenAI bilan xatolik yuz berdi: {e}")
else:
    st.warning("Iltimos, API kalitini va PDF faylni yuklang.")
