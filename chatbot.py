import streamlit as st
import google.generativeai as genai
import os

# 🔐 API Key Configuration
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDCZMHfKGZNyA-EmUzcBvTmqHvjSsv2hNQ")
genai.configure(api_key=API_KEY)

def generate_prompt_response(prompt):
    """Fetches AI-generated response from Google Gemini API."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "No response generated."
    except Exception as e:
        return f"🚨 Error: Unable to fetch response. Please try again later.\n\n**Details:** {str(e)}"

# 🟢 Initialize Streamlit App


st.title("💬 AI Stock Market Chatbot")
st.sidebar.header("📊 Market Assistant")

st.write("🚀 **Chat with AI about stocks, trends, or financial insights!**")

# 🛠️ Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 📌 User Input Field
user_prompt = st.text_input("💡 Type your question and press Enter:", key="user_input")

if user_prompt:
    # ⏳ Show a loading animation while processing
    with st.spinner("⏳ AI is thinking..."):
        ai_response = generate_prompt_response(user_prompt)
    
    # 📌 Append conversation to history
    st.session_state.chat_history.append(("user", user_prompt))
    st.session_state.chat_history.append(("ai", ai_response))
    
    # 🚀 Clear input field after submission
    st.text_input("💡 Type your question and press Enter:", key="user_input", value="")
    st.rerun()

# 📝 Display Chat History with message bubbles
st.write("### 🗨️ Conversation History")
for role, message in st.session_state.chat_history:
    if role == "user":
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                <div style="background-color: #e8f0fe; padding: 10px 15px; border-radius: 20px; max-width: 70%; word-wrap: break-word; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);">
                    {message}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                <div style="background-color: #f8f9fa; padding: 10px 15px; border-radius: 20px; max-width: 70%; word-wrap: break-word; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);">
                    {message}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# 🔄 Clear Chat Button
if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()