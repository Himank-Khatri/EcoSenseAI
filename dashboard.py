import streamlit as st
from datetime import datetime
from utils.utils import load_data, load_best_model, render_graph, show_pollutants, get_aqi_category, get_weather_info, get_ai_insights

with st.sidebar:
    st.header("Facility Profile")

    industry_type = st.text_input("Industry Type", value="Chemical")
    num_employees = st.number_input("Number of Employees", min_value=1, value=60, step=1)
    ventilation_type = st.selectbox("Ventilation Type", ["Natural", "Mechanical", "Hybrid"], index=0)
    shift_hours = st.slider("Shift Hours", min_value=4, max_value=16, value=8, step=1)

    business_description = st.text_area(
        "Business Description",
        value="We operate a chemical manufacturing facility that produces industrial solvents, coatings, and specialty chemicals. Our processes involve mixing, heating, and chemical reactions, which can release airborne pollutants like volatile organic compounds (VOCs), nitrogen oxides (NOx), and sulfur dioxide (SO₂). Our facility has mechanical ventilation with localized exhaust systems in high-risk areas, but some fumes may still accumulate indoors. We follow regulatory air quality standards, but we are looking for ways to further improve workplace safety, reduce emissions, and optimize air filtration systems. Employee safety is a priority, and we provide protective gear, such as respirators and gloves, but we want additional recommendations to ensure better air circulation, pollutant monitoring, and long-term health protection for workers.",
        height=180
    )

    st.markdown("💡 **These details will help tailor AI recommendations to your facility's needs.**")

    user_input = {
        "industry": industry_type,
        "employees": num_employees,
        "ventilation_type": ventilation_type,
        "shift_hours": shift_hours,
        "business_description": business_description
    }

col1, col_mid, col2 = st.columns([1.2, 0.1, 1])

with col1:
    with st.popover('Developer Settings'):
        hour = st.slider("Select Hour", min_value=1, max_value=100, value=1)

aqi_data, poll_data = load_data(hour)
current_aqi = aqi_data["Value"].iloc[-1]
category, emoji, color = get_aqi_category(current_aqi)

with col1:
    predictedions = render_graph(aqi_data)
    polls = show_pollutants(poll_data)

with col2:
    st.markdown(
        f"<h1 style='text-align: center; color: {color};'> {emoji} AQI: {current_aqi} ({category}) </h1>",
        unsafe_allow_html=True
    )

    st.markdown(f"<h4 style='text-align: center;'>📅 {datetime.now().strftime('%Y-%m-%d | %H:%M:%S')} </h4>", unsafe_allow_html=True)
    
    ai_container = st.container()
    weather_data = get_weather_info()

    with ai_container:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 🔍 AI Insights & Recommendations")
        # with st.spinner("Generating AI insights..."):
            # ai_insights = get_ai_insights(aqi_data, predictedions, polls, weather_data, user_input)

        # st.markdown(ai_insights, unsafe_allow_html=True)