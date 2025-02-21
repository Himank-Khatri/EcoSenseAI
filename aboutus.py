import streamlit as st
from PIL import Image

def resize_image(image_path, size=(300, 200)): 
    img = Image.open(image_path)
    img = img.resize(size)
    return img

col1, col2 = st.columns([1, 5])
with col1:
    st.image("images/logo.png", width=200) 


st.header("💡 Who We Are")
st.write("At **Eco Sense AI**, we combine **technology** and **sustainability** to create **smarter, healthier environments**. Our mission? To **analyze, predict, and improve air quality** using cutting-edge **sensor technology** and **artificial intelligence**! 🌱✨")

st.header("👩‍💻 Meet the Team")
st.write("Here’s the amazing team making it all happen! ")

c1, c2, c3 = st.columns([1,2,1]) 
with c2:
    with st.container(border=True):
        st.image("images/team_photo.jpg", caption="The Eco Sense AI Team!", use_container_width=True)

st.header("📊 What We Do")
st.write("We measure **real-time air quality** by detecting various pollutants and calculating the **Air Quality Index (AQI)**. But we don’t stop there! Our **AI-powered system** predicts future air quality trends and provides actionable recommendations. Here’s how it helps:")
st.markdown("- 🏠 **People on-site** stay informed and take necessary precautions for healthier living.")
st.markdown("- 🏢 **Companies** optimize environmental policies and improve workplace conditions for employees.")


st.title("🌿 Our Vision at Eco Sense AI")

st.write(
    "We believe that data-driven insights can lead to a cleaner, healthier future. "
    "By integrating AI with environmental monitoring, we empower businesses and individuals "
    "to take proactive steps toward sustainability."
)


col1, col2, col3 = st.columns(3)

# Panel 1
with col1:
    st.image(resize_image("images/vision1.jpg"), caption="📡 Monitoring Air Quality", use_container_width=True)
    st.markdown("<div style='text-align: center;'><b>Real-time Monitoring</b><br>AI-driven sensors detect pollution levels instantly.</div>", unsafe_allow_html=True)

# Panel 2
with col2:
    st.image(resize_image("images/vision2.jpg"), caption="🧠 AI-Based Predictions", use_container_width=True)
    st.markdown("<div style='text-align: center;'><b>AI Predictions</b><br>We use machine learning to forecast air quality trends.</div>", unsafe_allow_html=True)

# Panel 3
with col3:
    st.image(resize_image("images/vision3.jpg"), caption="🌍 Taking Action", use_container_width=True)
    st.markdown("<div style='text-align: center;'><b>Sustainable Impact</b><br>Helping businesses and communities make eco-friendly decisions.</div>", unsafe_allow_html=True)