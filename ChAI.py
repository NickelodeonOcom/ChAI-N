import streamlit as st
import g4f

# Function to generate chatbot response with memory
def get_response(user_input, chat_history, model_choice):
    try:
        response = g4f.ChatCompletion.create(
            model=model_choice,  
            messages=chat_history,  # Send entire chat history for memory
        )
        return response
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# Function to manage memory (limits conversation length)
def manage_memory(chat_history, max_tokens=4000):
    """
    Trims conversation history to fit within token limits.
    """
    total_tokens = sum(len(msg["content"]) for msg in chat_history)
    
    while total_tokens > max_tokens and len(chat_history) > 2:
        chat_history.pop(1)  # Remove oldest user message
        chat_history.pop(1)  # Remove oldest bot response
        total_tokens = sum(len(msg["content"]) for msg in chat_history)

# Streamlit UI
st.title("🤖 ChAI – Your Smart AI Companion")

# Sidebar settings
st.sidebar.header("⚙️ ChAI Settings")
model_choice = st.sidebar.selectbox(
    "Choose AI Model",
    options=[g4f.models.gpt_4, g4f.models.gpt_3_5, g4f.models.phind],  
    index=0
)
st.sidebar.markdown("💡 **GPT-4** remembers better but may be slower.")

# Chat memory initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are ChAI, a helpful AI assistant with memory."}
    ]

# Display chat history
for message in st.session_state.messages[1:]:  # Skip system prompt
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Type your message to ChAI...")

if user_input:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Manage memory (trim chat if needed)
    manage_memory(st.session_state.messages)

    # Show loading indicator
    with st.spinner("ChAI is thinking..."):
        bot_response = get_response(user_input, st.session_state.messages, model_choice)

    # Store chatbot response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Display chatbot response
    with st.chat_message("assistant"):
        st.markdown(bot_response)
