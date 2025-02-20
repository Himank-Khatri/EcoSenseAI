import streamlit as st
from datetime import datetime
from utils.utils import load_data, load_best_model, render_graph, show_pollutants, get_aqi_category, get_weather_info

# st.set_page_config(page_title='EcoSenseAI', layout='wide')


# def main():
# st.markdown("<h1>EcoSenseAI</h1>", unsafe_allow_html=True)

# st.markdown("<h5>What's in the air before it's there!</h5>", unsafe_allow_html=True)

col1, col_mid, col2 = st.columns([1.2, 0.1, 1])

with col1:
    with st.popover('Developer Settings'):
        hour = st.slider("Select Hour", min_value=1, max_value=100, value=1)

aqi_data, poll_data = load_data(hour)
current_aqi = aqi_data["Value"].iloc[-1]
category, emoji, color = get_aqi_category(current_aqi)

with col1:
    render_graph(aqi_data)
    show_pollutants(poll_data)

with col2:
    st.markdown(
        f"<h1 style='text-align: center; color: {color};'> {emoji} AQI: {current_aqi} ({category}) </h1>",
        unsafe_allow_html=True
    )

    st.markdown(f"<h4 style='text-align: center;'>📅 {datetime.now().strftime('%Y-%m-%d | %H:%M:%S')} </h4>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>🔍 AI Insights & Recommendations</h3>", unsafe_allow_html=True)

    st.write("### **Safety Measures**")
    st.write("- **Wear protective gear**: Use N95 masks in high AQI conditions.")
    st.write("- **Improve indoor air quality**: Use air purifiers, houseplants, and proper ventilation strategies.")
    st.write("- **Monitor health symptoms**: Respiratory issues can worsen with poor air quality; seek medical advice if needed.")

    st.write("### **Mitigation Strategies**")
    st.write("- **Industrial Compliance**: Enforce stricter emission controls and monitoring in industries like cement and steel manufacturing.")
    st.write("- **Sustainable Urban Planning**: Increase green zones, rooftop gardens, and urban forests to absorb pollutants.")

    get_weather_info()

# if __name__ == '__main__':
#     main()
