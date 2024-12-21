import streamlit as st
import pandas as pd
import random
import vertexai
from vertexai.preview.generative_models import GenerativeModel
import global_set as gb
import os
import json

gb.logo()

if st.button("ย้อนกลับ"):
    st.switch_page("/workspaces/6610424009_is/pages/streamlit_app.py")

st.markdown("#### เพื่อตอบคำถามถึงความสัมพันธ์ระหว่างคุณ และบุคคลอีกบุคคล")
st.write("ตัวอย่าง: นาย A รู้สึกยังไงกับเรา")
st.error("คำเตือน: ไม่ควรถามคำถามเดิมในช่วงเวลาเดียวกัน")
gb.ohm()
gb.focus()
TAROT_DATA_FILE = "/workspaces/6610424009_is/cards/023_cleaned_all_tarot_card_data.csv"
gb.survey()

# Set Google Cloud credentials and project
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/workspaces/6610424009_is/mutelu-chat.json"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mutelu-chat"
vertexai.init(project="mutelu-chat", location="asia-southeast1")

def draw_horseshoe_spread(tarot_data):
    """Draw 7 cards for Horseshoe Spread positions"""
    try:
        total_cards = len(tarot_data)
        random_numbers = random.sample(range(1, total_cards + 1), 7)
        
        spread_positions = {
            'past': None,               # Past influences
            'present': None,            # Present situation
            'hidden': None,             # Hidden influences
            'obstacles': None,          # Challenges
            'external': None,           # External influences
            'advice': None,             # Guidance
            'outcome': None             # Likely outcome
        }
        
        for position, num in zip(spread_positions.keys(), random_numbers):
            tarot_data_draw = tarot_data[tarot_data['card_no'] == num]
            if not tarot_data_draw.empty:
                spread_positions[position] = tarot_data_draw.iloc[0].to_dict()
        
        return spread_positions, random_numbers
    except Exception as e:
        st.error(f"Cannot draw cards: {e}")
        return None, None


def get_horseshoe_reading(question, card, position, sentiment):
    try:
        model = GenerativeModel("gemini-pro")
        
        position_prompts = {
            'past': f"""
            Past Position Card Reading:
            • Card drawn: {card['title']}
            • Focus on general past influences
            • Consider meaningful past experiences
            
            Response style:
            1. Must respond in Thai language
            2. Start with "ในอดีตที่ผ่านมา..."
            3. Keep interpretation under 4 sentences
            4. Use gentle and warm Thai language
            """,
            
            'present': f"""
            Present Position Card Reading:
            • Card drawn: {card['title']}
            • Focus on current energies and situations
            • Consider immediate circumstances
            
            Response style:
            1. Must respond in Thai language
            2. Start with "ในปัจจุบัน..."
            3. Keep interpretation under 4 sentences
            4. Use gentle and warm Thai language
            """,
            
            'hidden': f"""
            Hidden Influences Position:
            • Card drawn: {card['title']}
            • Focus on unseen factors
            • Consider subconscious influences
            
            Response style:
            1. Must respond in Thai language
            2. Start with "สิ่งที่ซ่อนอยู่..."
            3. Keep interpretation under 4 sentences
            4. Use gentle and warm Thai language
            """,
            
            'obstacles': f"""
            Obstacles Position:
            • Card drawn: {card['title']}
            • Focus on current challenges
            • Consider what needs attention
            
            Response style:
            1. Must respond in Thai language
            2. Start with "สิ่งที่ต้องระวังและใส่ใจ..."
            3. Keep interpretation under 4 sentences
            4. Be honest but constructive
            """,
            
            'external': f"""
            External Influences Position:
            • Card drawn: {card['title']}
            • Focus on outside factors
            • Consider environmental influences
            
            Response style:
            1. Must respond in Thai language
            2. Start with "ปัจจัยรอบตัว..."
            3. Keep interpretation under 4 sentences
            4. Use gentle and warm Thai language
            """,
            
            'advice': f"""
            Advice Position:
            • Card drawn: {card['title']}
            • Focus on guidance
            • Consider helpful actions
            
            Response style:
            1. Must respond in Thai language
            2. Start with "คำแนะนำ..."
            3. Keep advice clear and actionable
            4. End with encouragement
            """,
            
            'outcome': f"""
            Outcome Position:
            • Card drawn: {card['title']}
            • Focus on potential results
            • Consider future possibilities
            
            Response style:
            1. Must respond in Thai language
            2. Start with "แนวโน้มที่จะเกิดขึ้น..."
            3. Keep interpretation under 4 sentences
            4. End with hope and encouragement
            """
        }
        
        base_prompt = """
        You are a skilled tarot reader providing general insights in Thai language.
        Personality:
        • Use warm, gentle Thai language
        • Keep interpretations clear but meaningful
        • Balance honesty with encouragement
        • Be empathetic and supportive
        • Maintain a positive but realistic tone

        Important: Your response MUST be in Thai language and no emoji.
        """
        
        full_prompt = base_prompt + position_prompts[position]
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        st.error(f"ไม่สามารถสร้างคำทำนายได้: {e}")
        return None
 
    
def display_horseshoe_spread(cards, card_numbers):
    # Top row - Past, Present, Future (3 cards)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("### อดีต")
        st.write(f"**{cards['past']['title']}**")
        image_path = f"assets/card_{card_numbers[0]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
            
    with col2:
        st.write("### ปัจจุบัน")
        st.write(f"**{cards['present']['title']}**")
        image_path = f"assets/card_{card_numbers[1]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
    
    with col3:
        st.write("### อิทธิพลที่ซ่อนอยู่")
        st.write(f"**{cards['hidden']['title']}**")
        image_path = f"assets/card_{card_numbers[2]}.png"
        if os.path.exists(image_path):
            st.image(image_path)

    # Middle row - Challenges in center
    col1, col2, col3 = st.columns(3)
    with col2:
        st.write("### อุปสรรค")
        st.write(f"**{cards['obstacles']['title']}**")
        image_path = f"assets/card_{card_numbers[3]}.png"
        if os.path.exists(image_path):
            st.image(image_path)

    # Bottom row - External, Advice, Outcome
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("### อิทธิพลภายนอก")
        st.write(f"**{cards['external']['title']}**")
        image_path = f"assets/card_{card_numbers[4]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
            
    with col2:
        st.write("### คำแนะนำ")
        st.write(f"**{cards['advice']['title']}**")
        image_path = f"assets/card_{card_numbers[5]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
            
    with col3:
        st.write("### ผลลัพธ์")
        st.write(f"**{cards['outcome']['title']}**")
        image_path = f"assets/card_{card_numbers[6]}.png"
        if os.path.exists(image_path):
            st.image(image_path)

def main():
    # Add spread type selection
    spread_type = "Horseshoe Spread (7 ใบ)"
    
    tarot_data = gb.fetch_local_tarot_data()
    
    if st.button("ทำนายดวง"):
        st.write(" รอสักครู่ คำทำนายกำลังมา ...")
        if tarot_data is not None:
            cards, card_numbers = draw_horseshoe_spread(tarot_data)
            
            if cards:
                # Display horseshoe spread layout
                display_horseshoe_spread(cards, card_numbers)
                
                # Display reading
                st.markdown("---")
                st.write("## การทำนาย 🔮")
                
                positions = ['past', 'present', 'hidden', 'obstacles', 'external', 'advice', 'outcome']
                for position in positions:
                    prediction = get_horseshoe_reading(
                        "",  # No question needed
                        cards[position],
                        position,
                        "NEUTRAL"  # Default sentiment since no question
                    )
                    if prediction:
                        st.write(prediction)
                        if position != 'outcome':
                            st.markdown("---")
        gb.end_predict()

if __name__ == "__main__":
    main()