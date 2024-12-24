import streamlit as st
import pandas as pd
import random
import vertexai
from vertexai.preview.generative_models import GenerativeModel
import global_set as gb
import os
import json

gb.logo()
gb.api_key()

if st.button("ย้อนกลับ"):
    st.switch_page("/workspaces/6610424009_is/pages/streamlit_app.py")

st.markdown("#### เพื่อทำนายอนาคตแต่ละเดือน 12 เดือนต่อจากนี้")
gb.focus('no input')
TAROT_DATA_FILE = "/workspaces/6610424009_is/023_cleaned_all_tarot_card_data.csv"
st.error("คำเตือน: ควรทำนายแค่เดือนละ 1 ครั้ง")

# Set Google Cloud credentials and project
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/workspaces/6610424009_is/mutelu-chat.json"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mutelu-chat"
vertexai.init(project="mutelu-chat", location="asia-southeast1")

def draw_year_ahead_spread(tarot_data):
    """Draw 13 cards for Year Ahead Spread - 12 months plus central theme"""
    try:
        total_cards = len(tarot_data)
        random_numbers = random.sample(range(1, total_cards + 1), 13)
        
        spread_positions = {
            'theme': None,      # Central theme for the year
            'january': None,    # January
            'february': None,   # February
            'march': None,      # March
            'april': None,      # April
            'may': None,        # May
            'june': None,       # June
            'july': None,       # July
            'august': None,     # August
            'september': None,  # September
            'october': None,    # October
            'november': None,   # November
            'december': None    # December
        }
        
        for position, num in zip(spread_positions.keys(), random_numbers):
            tarot_data_draw = tarot_data[tarot_data['card_no'] == num]
            if not tarot_data_draw.empty:
                spread_positions[position] = tarot_data_draw.iloc[0].to_dict()
        
        return spread_positions, random_numbers
    except Exception as e:
        st.error(f"Cannot draw cards: {e}")
        return None, None

def display_year_ahead_spread(cards, card_numbers):
    # Center theme card
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("### ธีมหลักของปี")
        st.write(f"**{cards['theme']['title']}**")
        image_path = f"assets/card_{card_numbers[0]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
    
    st.markdown("---")
    st.write("## ไพ่ประจำแต่ละเดือน")

    # First quarter (Jan-Mar)
    col1, col2, col3 = st.columns(3)
    months_q1 = [('january', 'มกราคม'), ('february', 'กุมภาพันธ์'), ('march', 'มีนาคม')]
    
    for (month_key, month_name), col in zip(months_q1, [col1, col2, col3]):
        with col:
            st.write(f"### เดือน{month_name}")
            st.write(f"**{cards[month_key]['title']}**")
            image_path = f"assets/card_{card_numbers[list(cards.keys()).index(month_key)]}.png"
            if os.path.exists(image_path):
                st.image(image_path)

    # Second quarter (Apr-Jun)
    col1, col2, col3 = st.columns(3)
    months_q2 = [('april', 'เมษายน'), ('may', 'พฤษภาคม'), ('june', 'มิถุนายน')]
    
    for (month_key, month_name), col in zip(months_q2, [col1, col2, col3]):
        with col:
            st.write(f"### เดือน{month_name}")
            st.write(f"**{cards[month_key]['title']}**")
            image_path = f"assets/card_{card_numbers[list(cards.keys()).index(month_key)]}.png"
            if os.path.exists(image_path):
                st.image(image_path)

    # Third quarter (Jul-Sep)
    col1, col2, col3 = st.columns(3)
    months_q3 = [('july', 'กรกฎาคม'), ('august', 'สิงหาคม'), ('september', 'กันยายน')]
    
    for (month_key, month_name), col in zip(months_q3, [col1, col2, col3]):
        with col:
            st.write(f"### เดือน{month_name}")
            st.write(f"**{cards[month_key]['title']}**")
            image_path = f"assets/card_{card_numbers[list(cards.keys()).index(month_key)]}.png"
            if os.path.exists(image_path):
                st.image(image_path)

    # Fourth quarter (Oct-Dec)
    col1, col2, col3 = st.columns(3)
    months_q4 = [('october', 'ตุลาคม'), ('november', 'พฤศจิกายน'), ('december', 'ธันวาคม')]
    
    for (month_key, month_name), col in zip(months_q4, [col1, col2, col3]):
        with col:
            st.write(f"### เดือน{month_name}")
            st.write(f"**{cards[month_key]['title']}**")
            image_path = f"assets/card_{card_numbers[list(cards.keys()).index(month_key)]}.png"
            if os.path.exists(image_path):
                st.image(image_path)
def get_year_ahead_reading(card, position):
    try:
        model = GenerativeModel("gemini-pro")
        
        # Convert month keys to Thai month names
        month_names = {
            'theme': 'ธีมหลักของปี',
            'january': 'มกราคม',
            'february': 'กุมภาพันธ์',
            'march': 'มีนาคม',
            'april': 'เมษายน',
            'may': 'พฤษภาคม',
            'june': 'มิถุนายน',
            'july': 'กรกฎาคม',
            'august': 'สิงหาคม',
            'september': 'กันยายน',
            'october': 'ตุลาคม',
            'november': 'พฤศจิกายน',
            'december': 'ธันวาคม'
        }
        
        if position == 'theme':
            prompt = f"""
            Year Theme Card:
            • Card drawn: {card['title']}
            • Focus on overall energy for the year
            • Consider main themes and influences
            
            Response style:
            1. Must respond in Thai language
            2. Start with "ธีมหลักของปีนี้..."
            3. Keep interpretation under 4 sentences
            4. Provide overall guidance
            """
        else:
            prompt = f"""
            Monthly Card for {month_names[position]}:
            • Card drawn: {card['title']}
            • Focus on energy for this month
            • Consider events and influences
            
            Response style:
            1. Must respond in Thai language
            2. Start with "ในเดือน{month_names[position]}..."
            3. Keep interpretation under 4 sentences
            4. Provide specific guidance
            """
        
        base_prompt = """
        You are a skilled tarot reader providing yearly forecast insights in Thai language.
        Personality:
        • Use warm, gentle Thai language
        • Keep interpretations clear but meaningful
        • Balance honesty with encouragement
        • Be empathetic and supportive

        Important: Your response MUST be in Thai language only.
        """
        
        full_prompt = base_prompt + prompt
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        st.error(f"ไม่สามารถสร้างคำทำนายได้: {e}")
        return None

def get_year_ahead_summary(cards):
    try:
        model = GenerativeModel("gemini-pro")
        
        summary_prompt = f"""
        Create a comprehensive summary of the year ahead based on all 13 cards.
        
        Theme: {cards['theme']['title']}
        
        Monthly progression:
        January: {cards['january']['title']}
        February: {cards['february']['title']}
        March: {cards['march']['title']}
        April: {cards['april']['title']}
        May: {cards['may']['title']}
        June: {cards['june']['title']}
        July: {cards['july']['title']}
        August: {cards['august']['title']}
        September: {cards['september']['title']}
        October: {cards['october']['title']}
        November: {cards['november']['title']}
        December: {cards['december']['title']}

        Guidelines:
        1. Must respond in Thai language
        2. Start with "สรุปภาพรวมของปีที่จะมาถึง..."
        3. Include:
           - Overall theme and energy
           - Key periods or transitions
           - Major opportunities or challenges
           - Seasonal patterns
        4. Keep to 6-8 sentences
        5. End with guidance for navigating the year ahead
        6. Use gentle and warm Thai language

        Response format: 
        - Write as a cohesive paragraph
        - Connect different parts of the year
        - Highlight important trends
        - Provide practical guidance
        """

        response = model.generate_content(summary_prompt)
        return response.text

    except Exception as e:
        st.error(f"ไม่สามารถสร้างสรุปได้: {e}")
        return None
    
def get_year_theme_summary(cards):
    try:
        model = GenerativeModel("gemini-pro")
        
        summary_prompt = f"""
        Create a comprehensive yearly forecast based on the theme card and 12 monthly cards.

        Theme Card: {cards['theme']['title']}
        This card represents the overarching energy and theme for the entire year.

        Guidelines:
        1. Must respond in Thai language
        2. Start with "จากไพ่ {cards['theme']['title']} ที่เป็นธีมหลักของปี..."
        3. Focus interpretation on:
           - How the theme card influences each quarter
           - Key opportunities based on theme
           - Main challenges to be aware of
           - How to best work with this energy
        4. Keep to 5-6 sentences
        5. Use gentle and warm Thai language
        6. End with practical guidance for the year

        Important:
        - Focus mainly on the theme card's influence
        - Show how this energy manifests throughout the year
        - Keep interpretation encouraging but realistic
        - Provide actionable advice based on the theme
        """

        response = model.generate_content(summary_prompt)
        return response.text

    except Exception as e:
        st.error(f"ไม่สามารถสร้างสรุปได้: {e}")
        return None

def main():
    
    tarot_data = gb.fetch_local_tarot_data()
    
    if st.button("ทำนายดวง"):
        st.write(" รอสักครู่ คำทำนายกำลังมา ...")
        if tarot_data is not None:
            cards, card_numbers = draw_year_ahead_spread(tarot_data)
            
            if cards:
                # Display year ahead spread layout
                display_year_ahead_spread(cards, card_numbers)
                
                # Display theme reading first
                st.markdown("---")
                # Display monthly readings
                st.write("## คำทำนายรายเดือน 📅")
                months = ['january', 'february', 'march', 'april', 'may', 'june',
                         'july', 'august', 'september', 'october', 'november', 'december']
                
                for month in months:
                    prediction = get_year_ahead_reading(cards[month], month)
                    predictions = {
                    "theme": prediction,
                    "monthly": {}
                }
                    if prediction:
                        st.write(prediction)
                        predictions['monthly'][month] = prediction
                        if month != 'december':

                            st.markdown("---")

                                # Display theme-based summary
                st.markdown("---")
                st.write("## สรุปภาพรวมแต่ละเดือน")
                summary = get_year_ahead_summary(cards)
                predictions['summary'] = summary
                if summary:
                    st.write(summary)

                st.markdown("---")
                st.write("## สรุปภาพรวมทั้งปี")
                summary = get_year_theme_summary(cards)
                if summary:
                    st.write(summary)
                user_input = {
                    "reading_type": "year_ahead"
                }
                
                gb.save_reading_log(
                    user_input=user_input,
                    reading_type="year_ahead",
                    cards_drawn=cards,
                    predictions=predictions
                )

        gb.end_predict()
        gb.survey()
if __name__ == "__main__":
    main()