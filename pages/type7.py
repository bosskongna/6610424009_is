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

st.markdown("#### การทำนายด้วยไพ่ 10 ใบ แสดงถึงสถานการณ์ปัจจุบัน สิ่งที่ท้าทาย เป้าหมาย รากฐาน อดีต อนาคต ตัวคุณ สิ่งรอบตัว ความหวัง และผลลัพธ์")
gb.focus('no input')
TAROT_DATA_FILE = "/workspaces/6610424009_is/023_cleaned_all_tarot_card_data.csv"
st.error("คำเตือน: หากเคยได้รับคำทำนายไปแล้ว ควรเว้นระยะอย่างน้อย 2 อาทิตย์")

# Set Google Cloud credentials and project
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/workspaces/6610424009_is/mutelu-chat.json"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mutelu-chat"
vertexai.init(project="mutelu-chat", location="asia-southeast1")

def draw_celtic_cross(tarot_data):
    """Draw 10 unique cards for Celtic Cross positions"""
    try:
        total_cards = len(tarot_data)
        random_numbers = random.sample(range(1, total_cards + 1), 10)
        
        spread_positions = {
            'present': None,      # Card 1: Present situation
            'challenge': None,    # Card 2: Immediate challenge/crossing
            'above': None,        # Card 3: Crowning (above)
            'below': None,        # Card 4: Foundation (below)
            'past': None,         # Card 5: Recent past
            'future': None,       # Card 6: Near future
            'self': None,         # Card 7: Your attitude
            'external': None,     # Card 8: External influences
            'hopes': None,        # Card 9: Hopes and fears
            'outcome': None       # Card 10: Final outcome
        }
        
        for position, num in zip(spread_positions.keys(), random_numbers):
            tarot_data_draw = tarot_data[tarot_data['card_no'] == num]
            if not tarot_data_draw.empty:
                spread_positions[position] = tarot_data_draw.iloc[0].to_dict()
        
        return spread_positions, random_numbers
    except Exception as e:
        st.error(f"Cannot draw cards: {e}")
        return None, None

def get_celtic_cross_reading(card, position):
    try:
        model = GenerativeModel("gemini-pro")
        
        position_prompts = {
            'present': f"""
            Present Position (Card 1):
            • Card drawn: {card['title']}
            • Focus on current situation
            • Describe what's happening right now
            
            Response style:
            1. Must respond in Thai language
            2. Start with "สิ่งที่ท้าทายในตอนนี้..."
            3. Keep interpretation under 4 sentences
            4. Use gentle and warm Thai language
            """,
            
            'challenge': f"""
            Challenge Position (Card 2):
            • Card drawn: {card['title']}
            • Focus on immediate obstacles
            • Describe current difficulties
            
            Response style:
            1. Must respond in Thai language
            2. Start with "สิ่งที่ท้าทาย..."
            3. Keep interpretation under 4 sentences
            4. Be honest but constructive
            """,
            
            'above': f"""
            Above Position (Card 3):
            • Card drawn: {card['title']}
            • Focus on goals and aspirations
            • Describe best possible outcomes
            
            Response style:
            1. Must respond in Thai language
            2. Start with "สิ่งที่เป็นไปได้..."
            3. Keep interpretation under 4 sentences
            4. Be optimistic but realistic
            """,
            
            'below': f"""
            Below Position (Card 4):
            • Card drawn: {card['title']}
            • Focus on foundation and roots
            • Describe underlying influences
            
            Response style:
            1. Must respond in Thai language
            2. Start with "รากฐานที่สำคัญ..."
            3. Keep interpretation under 4 sentences
            4. Be clear and insightful
            """,
            
            'past': f"""
            Past Position (Card 5):
            • Card drawn: {card['title']}
            • Focus on recent past events
            • Describe relevant history
            
            Response style:
            1. Must respond in Thai language
            2. Start with "สิ่งที่ผ่านมา..."
            3. Keep interpretation under 4 sentences
            4. Connect past to present
            """,
            
            'future': f"""
            Future Position (Card 6):
            • Card drawn: {card['title']}
            • Focus on coming influences
            • Describe potential developments
            
            Response style:
            1. Must respond in Thai language
            2. Start with "สิ่งที่กำลังจะมาถึง..."
            3. Keep interpretation under 4 sentences
            4. Be hopeful but balanced
            """,
            
            'self': f"""
            Self Position (Card 7):
            • Card drawn: {card['title']}
            • Focus on personal attitudes
            • Describe inner state
            
            Response style:
            1. Must respond in Thai language
            2. Start with "สภาวะภายในของคุณ..."
            3. Keep interpretation under 4 sentences
            4. Be understanding and supportive
            """,
            
            'external': f"""
            External Position (Card 8):
            • Card drawn: {card['title']}
            • Focus on outside influences
            • Describe environmental factors
            
            Response style:
            1. Must respond in Thai language
            2. Start with "สิ่งแวดล้อมรอบตัว..."
            3. Keep interpretation under 4 sentences
            4. Consider external impacts
            """,
            
            'hopes': f"""
            Hopes/Fears Position (Card 9):
            • Card drawn: {card['title']}
            • Focus on hopes and fears
            • Describe emotional expectations
            
            Response style:
            1. Must respond in Thai language
            2. Start with "ความหวังและความกังวล..."
            3. Keep interpretation under 4 sentences
            4. Balance hopes and concerns
            """,
            
            'outcome': f"""
            Outcome Position (Card 10):
            • Card drawn: {card['title']}
            • Focus on likely outcomes
            • Describe final results
            
            Response style:
            1. Must respond in Thai language
            2. Start with "ผลลัพธ์สุดท้าย..."
            3. Keep interpretation under 4 sentences
            4. End with encouragement
            """
        }
        
        base_prompt = """
        You are a skilled tarot reader providing Celtic Cross spread insights in Thai language.
        Personality:
        • Use warm, gentle Thai language
        • Keep interpretations clear but meaningful
        • Balance honesty with encouragement
        • Be empathetic and supportive

        Important: Your response MUST be in Thai language only.
        Do not include any English words or phrases in the response.
        """
        
        full_prompt = base_prompt + position_prompts.get(position, position_prompts['present'])
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        st.error(f"ไม่สามารถสร้างคำทำนายได้: {e}")
        return None
    
def get_celtic_cross_summary(cards):
    try:
        model = GenerativeModel("gemini-pro")
        
        summary_prompt = f"""
        Create a comprehensive summary of this 10-card Celtic Cross spread reading.
        
        Cards drawn:
        1. Present: {cards['present']['title']} (สถานการณ์ปัจจุบัน)
        2. Challenge: {cards['challenge']['title']} (สิ่งที่ท้าทาย)
        3. Above: {cards['above']['title']} (สิ่งที่อยู่เหนือ/เป้าหมาย)
        4. Below: {cards['below']['title']} (รากฐาน)
        5. Past: {cards['past']['title']} (อดีต)
        6. Future: {cards['future']['title']} (อนาคต)
        7. Self: {cards['self']['title']} (ตัวคุณ)
        8. External: {cards['external']['title']} (สิ่งรอบตัว)
        9. Hopes/Fears: {cards['hopes']['title']} (ความหวังและความกลัว)
        10. Outcome: {cards['outcome']['title']} (ผลลัพธ์)

        Guidelines:
        1. Must respond in Thai language
        2. Start with "สรุปภาพรวมจากไพ่ทั้ง 10 ใบ..."
        3. Create a flowing narrative connecting all cards
        4. Consider the relationship between:
           - Present situation and its challenges
           - Foundation and goals
           - Past influences and future direction
           - Internal and external factors
           - Hopes/fears and final outcome
        5. Keep to 6-8 sentences maximum
        6. End with encouraging guidance
        7. Use gentle and warm Thai language

        Response format: 
        - Write as a cohesive paragraph
        - Weave card meanings together naturally
        - Maintain a balanced and insightful tone
        - Focus on overall story and guidance
        """

        response = model.generate_content(summary_prompt)
        return response.text

    except Exception as e:
        st.error(f"ไม่สามารถสร้างสรุปได้: {e}")
        return None
 
def display_celtic_cross(cards, card_numbers):
    # Center column for the cross
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # Above card
    with col2:
        st.write("### สิ่งที่อยู่เหนือ")
        st.write(f"**{cards['above']['title']}**")
        image_path = f"assets/card_{card_numbers[2]}.png"
        if os.path.exists(image_path):
            st.image(image_path)

    # Middle row - Past, Present/Challenge, Future
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("### อดีต")
        st.write(f"**{cards['past']['title']}**")
        image_path = f"assets/card_{card_numbers[4]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
    
    with col2:
        # Present and Challenge cards side by side
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.write("### ปัจจุบัน")
            st.write(f"**{cards['present']['title']}**")
            image_path = f"assets/card_{card_numbers[0]}.png"
            if os.path.exists(image_path):
                st.image(image_path)
        with subcol2:
            st.write("### สิ่งท้าทาย")
            st.write(f"**{cards['challenge']['title']}**")
            image_path = f"assets/card_{card_numbers[1]}.png"
            if os.path.exists(image_path):
                st.image(image_path)
    
    with col3:
        st.write("### อนาคต")
        st.write(f"**{cards['future']['title']}**")
        image_path = f"assets/card_{card_numbers[5]}.png"
        if os.path.exists(image_path):
            st.image(image_path)

    # Below card
    with col2:
        st.write("### รากฐาน")
        st.write(f"**{cards['below']['title']}**")
        image_path = f"assets/card_{card_numbers[3]}.png"
        if os.path.exists(image_path):
            st.image(image_path)

    # Staff column (right side column)
    st.markdown("---")
    st.write("## แนวโน้มและผลลัพธ์")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.write("### ตัวคุณ")
        st.write(f"**{cards['self']['title']}**")
        image_path = f"assets/card_{card_numbers[6]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
            
    with col2:
        st.write("### สิ่งรอบตัว")
        st.write(f"**{cards['external']['title']}**")
        image_path = f"assets/card_{card_numbers[7]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
            
    with col3:
        st.write("### ความหวังและความกลัว")
        st.write(f"**{cards['hopes']['title']}**")
        image_path = f"assets/card_{card_numbers[8]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
            
    with col4:
        st.write("### ผลลัพธ์")
        st.write(f"**{cards['outcome']['title']}**")
        image_path = f"assets/card_{card_numbers[9]}.png"
        if os.path.exists(image_path):
            st.image(image_path)

def main():
    # Simple title and description
    
    tarot_data = gb.fetch_local_tarot_data()
    
    if st.button("ทำนายดวง"):
        st.write(" รอสักครู่ คำทำนายกำลังมา ...")
        if tarot_data is not None:
            # Draw cards for Celtic Cross spread
            cards, card_numbers = draw_celtic_cross(tarot_data)
            
            if cards:
                # Display Celtic Cross layout
                display_celtic_cross(cards, card_numbers)
                
                # Display reading
                st.markdown("---")
                st.write("## การทำนาย 🔮")
                
                # Define reading order
                positions = ['present', 'challenge', 'above', 'below', 'past', 
                           'future', 'self', 'external', 'hopes', 'outcome']
                predictions = {}
                # Get reading for each position
                for position in positions:
                    prediction = get_celtic_cross_reading(
                        cards[position],
                        position
                    )
                    predictions[position] = prediction
                    if prediction:
                        st.write(prediction)
                        if position != 'outcome':
                            st.markdown("---")
                
                # Add overall summary
                st.markdown("---")
                st.write("## สรุปภาพรวมไพ่ทั้งหมด 🔮")
                summary = get_celtic_cross_summary(cards)
                if summary:
                    st.write(summary)
                    user_input = {
                    "reading_type": "celtic_cross"
                }
                    gb.save_reading_log(
                        user_input=user_input,
                        reading_type="celtic_cross",
                        cards_drawn=cards,
                        predictions=predictions
                    )
        gb.end_predict()
        gb.survey()

if __name__ == "__main__":
    main()