import os
import streamlit as st
import ollama

# Enable GPU for Ollama
os.environ["OLLAMA_USE_GPU"] = "1"

# Set up Streamlit app
st.set_page_config(page_title="EcoBot - Your Climate Companion", layout="wide")

# Layout with image and title
col1, col2 = st.columns([1, 5])
with col1:
    st.image(r"C:\Users\Farhan\Downloads\Screenshot_2025-02-20_120503-removebg-preview.png", width=150)  # Custom logo on the left
with col2:
    st.title("EcoBot - Your Climate Companion ")
    # st.markdown("""
    # ### 
    # """)

# Divider
st.markdown("---")

# System Prompt (Defines Bot’s Knowledge)
system_prompt = """
You are a highly knowledgeable AI assistant specializing in climate science, air quality, and environmental sustainability.
Your goal is to provide accurate, science-backed, and up-to-date information.

*Topics you should answer:*
- Climate change, air quality, renewable energy, carbon emissions, sustainability
- Global and regional climate policies (Paris Agreement, IPCC reports, COP conferences)
- Extreme weather events, deforestation, urbanization, industrial emissions

*Topics you should NOT answer:*
- Politics, entertainment, sports, AI development, personal finance, medicine, space, and unrelated science topics.

*How to respond to unrelated questions:*
"Sorry, I can only answer climate, air quality, and sustainability-related questions."

*Your response style:*
- Provide factual, science-based information with real-world examples.
- Offer practical solutions for climate-related concerns.
- Avoid opinions—stick to evidence-based knowledge.
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Welcome to EcoBot!\n\nI'm here to provide reliable, science-backed insights on climate change, air quality, and sustainability.\n\nAsk me about:\n- Global warming\n- Renewable energy\n- Carbon footprints\n- Ways to live more sustainably\n\nLet's work together for a greener future! 🌱"}

    ]

# Display chat history (excluding system prompt)
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue  # Skip system prompt from display
    with st.chat_message(msg["role"]):
        if "<think>" in msg["content"]:
            response_parts = msg["content"].split("</think>")
            reasoning = response_parts[0].replace("<think>", "").strip()
            final_response = response_parts[-1].strip()
            st.markdown(final_response)
            with st.expander("🔍 Show Reasoning", expanded=False):
                st.markdown(f"🤖 Reasoning:** {reasoning}")
        else:
            st.markdown(msg["content"])

# User input
user_input = st.chat_input("Type your message...")

if user_input:
    # Append user input to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user input in chat
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get response from Ollama model
    with st.spinner("Thinking..."):
        try:
            response = ollama.chat(model="my-llama3", messages=st.session_state.messages)
            bot_response = response["message"]["content"]  # Extract response
        except Exception as e:
            bot_response = f"⚠ Error: {str(e)}"

    # Append bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Display bot response in chat
    with st.chat_message("assistant"):
        if "<think>" in bot_response:
            response_parts = bot_response.split("</think>")
            reasoning = response_parts[0].replace("<think>", "").strip()
            final_response = response_parts[-1].strip()
            st.markdown(final_response)
            with st.expander("🔍 Show Reasoning", expanded=False):
                st.markdown(f"🤖 Reasoning:** {reasoning}")
        else:
            st.markdown(bot_response)