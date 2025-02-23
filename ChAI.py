import streamlit as st
import g4f
import pyttsx3  # Text-to-Speech
import speech_recognition as sr  # Voice Input
import tempfile
import os

# Initialize TTS Engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand."
    except sr.RequestError:
        return "Speech recognition service unavailable."

def get_response(user_input, chat_history, model_choice):
    try:
        response = g4f.ChatCompletion.create(
            model=model_choice,
            messages=chat_history,  # Send chat history for memory
        )
        return response
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def manage_memory(chat_history, max_tokens=4000):
    total_tokens = sum(len(msg["content"]) for msg in chat_history)
    while total_tokens > max_tokens and len(chat_history) > 2:
        chat_history.pop(1)  # Remove oldest user message
        chat_history.pop(1)  # Remove oldest bot response
        total_tokens = sum(len(msg["content"]) for msg in chat_history)

# UI Setup
st.set_page_config(page_title="ChAI - AI Chatbot", page_icon="🤖", layout="wide")
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #1e1e2e;
            color: white;
        }
        .chat-container {
            max-width: 800px;
            margin: auto;
            padding: 20px;
        }
        .user-message {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            text-align: right;
            animation: fadeIn 0.5s ease-in-out;
        }
        .bot-message {
            background-color: #333;
            color: white;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            text-align: left;
            animation: fadeIn 0.5s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 ChAI - Your Smart AI Assistant")
st.markdown("---")

# Sidebar settings
st.sidebar.header("⚙️ Settings")
model_choice = st.sidebar.selectbox(
    "Choose AI Model",
    options=[g4f.models.gpt_4, g4f.models.gpt_4o, g4f.models.gpt_4o_mini],
    index=0
)
st.sidebar.markdown("💡 **GPT-4** is smarter but may be slower.")

# Toggle memory storage
enable_memory = st.sidebar.checkbox("Enable Conversation Memory", value=True)

# File Upload Feature
uploaded_file = st.sidebar.file_uploader("📂 Upload a File (TXT/PDF)", type=["txt", "pdf"])
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(uploaded_file.getvalue())
        temp_path = temp.name
    with open(temp_path, "r", encoding="utf-8") as f:
        file_content = f.read()
    os.remove(temp_path)
    st.sidebar.success("📄 File processed successfully!")
else:
    file_content = ""

# Chat memory initialization
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are ChAI, a helpful AI assistant with memory."}]

# Display chat history
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for message in st.session_state.messages[1:]:  # Skip system prompt
    role_class = "user-message" if message["role"] == "user" else "bot-message"
    st.markdown(f"<div class='{role_class}'>{message['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# User input options (Text & Voice)
user_input = st.text_input("💬 Type your message:", "")
if st.button("🎙️ Speak"):
    user_input = listen()
    st.text(f"🎤 You said: {user_input}")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    manage_memory(st.session_state.messages)
    with st.spinner("🤖 ChAI is thinking..."):
        bot_response = get_response(user_input, st.session_state.messages, model_choice)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.markdown(f"<div class='bot-message'>{bot_response}</div>", unsafe_allow_html=True)
    if st.sidebar.checkbox("🔊 Enable Text-to-Speech", value=False):
        speak(bot_response)
