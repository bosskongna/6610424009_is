import streamlit as st
import pandas as pd
import random
import vertexai
from vertexai.preview.generative_models import GenerativeModel
import global_set as gb
import os
import json

gb.logo()
gb.initialize_vertexai()  # Initialize Vertex
bucket = gb.initialize_gcs()  # Initialize GC AI


gb.button_main_page()

st.markdown("#### การทำนายด้วยไพ่อย่างละ 3 ใบ ต่อ 1 ตัวเลือก ")
gb.focus('input')
TAROT_DATA_FILE = "/workspaces/6610424009_is/023_cleaned_all_tarot_card_data.csv"
st.error("คำเตือน: หากเคยได้รับคำทำนายไปแล้ว ควรเว้นระยะอย่างน้อย 2 อาทิตย์")

# Set Google Cloud credentials and project
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/workspaces/6610424009_is/mutelu-chat.json"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mutelu-chat"
vertexai.init(project="mutelu-chat", location="asia-southeast1")

def draw_comparison_spread(tarot_data, num_choices):
    """Draw 3 cards for each choice"""
    try:
        cards_per_choice = 3
        total_cards_needed = num_choices * cards_per_choice
        random_numbers = random.sample(range(1, len(tarot_data) + 1), total_cards_needed)
        
        spread_positions = {}
        for i in range(num_choices):
            choice_key = f'choice{i+1}'
            spread_positions[choice_key] = {
                'opportunity': None,  # Positive aspects/opportunities
                'challenge': None,    # Challenges/considerations
                'outcome': None       # Likely outcome
            }
        
        # Distribute cards to positions
        card_index = 0
        for choice in spread_positions.keys():
            for position in ['opportunity', 'challenge', 'outcome']:
                tarot_data_draw = tarot_data[tarot_data['card_no'] == random_numbers[card_index]]
                if not tarot_data_draw.empty:
                    spread_positions[choice][position] = tarot_data_draw.iloc[0].to_dict()
                card_index += 1
        
        return spread_positions, random_numbers
    except Exception as e:
        st.error(f"Cannot draw cards: {e}")
        return None, None
    
def get_comparison_reading(cards,question_input, choice_names):
    try:
        model = GenerativeModel("gemini-1.5-flash-002")
        
        # Create detailed choice descriptions for the prompt
        choices_desc = ""
        for i, (choice, name) in enumerate(zip(cards.keys(), choice_names)):
            choices_desc += f"""
            Choice {i+1}: {name}
            - Opportunity: {cards[choice]['opportunity']['title']}
            - Challenge: {cards[choice]['challenge']['title']}
            - Outcome: {cards[choice]['outcome']['title']}
            """
        
        summary_prompt = f"""
        Analyze these options based on their tarot cards and provide a comparison based on {question_input}.

        {choices_desc}

        Guidelines:
        1. Must respond in Thai language
        2. Start with "จากการวิเคราะห์ไพ่ทั้งหมด..."
        3. For each option:
           - Describe its main strengths and challenges
           - Evaluate its potential outcome
        4. Compare all options
        5. Rank them from most to least favorable
        6. Explain the reasoning behind the ranking
        7. Provide practical guidance for making the choice

        Response format:
        1. Individual analysis of each option
        2. Comparison and ranking
        3. Final recommendation
        4. Keep total response to 8-10 sentences
        5. Use gentle and warm Thai language
        6. No emoji
        """

        response = model.generate_content(summary_prompt)
        return response.text

    except Exception as e:
        st.error(f"ไม่สามารถสร้างการวิเคราะห์ได้: {e}")
        return None
 
def display_comparison_spread(cards, card_numbers, choice_names):
    card_index = 0
    
    for i, choice in enumerate(cards.keys()):
        st.write(f"## ทางเลือกที่ {i+1}: {choice_names[i]}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("### โอกาส")
            st.write(f"**{cards[choice]['opportunity']['title']}**")
            image_path = f"assets/card_{card_numbers[card_index]}.png"
            if os.path.exists(image_path):
                st.image(image_path)
                
        with col2:
            st.write("### ความท้าทาย")
            st.write(f"**{cards[choice]['challenge']['title']}**")
            image_path = f"assets/card_{card_numbers[card_index + 1]}.png"
            if os.path.exists(image_path):
                st.image(image_path)
                
        with col3:
            st.write("### ผลลัพธ์")
            st.write(f"**{cards[choice]['outcome']['title']}**")
            image_path = f"assets/card_{card_numbers[card_index + 2]}.png"
            if os.path.exists(image_path):
                st.image(image_path)
        
        card_index += 3
        st.markdown("---")

def main():
    st.markdown("#### เปิดไพ่เพื่อเปรียบเทียบทางเลือก")
    st.write("เปิดไพ่ 3 ใบต่อ 1 ทางเลือก เพื่อดูโอกาส ความท้าทาย และผลลัพธ์")
    
    # Dropdown for number of choices
    num_choices = st.selectbox(
        "เลือกจำนวนสิ่งที่ต้องการเปรียบเทียบ",
        options=[2, 3, 4, 5],
        help="เลือกจำนวนสิ่งที่ต้องการเปรียบเทียบ (2-5)"
    )
    
    # Single text input for all choices
    question_input = st.text_input("ใส่คำถามที่ต้องการเปรียบเทียบ\
                                   ตัวอย่าง: ทำงานที่ไหนแล้วมีความสุขมากกว่ากัน, คบคนไหนดี")
    choices_input = st.text_input(
        f"ใส่ชื่อสิ่งที่ต้องการเปรียบเทียบ {num_choices} อย่าง (คั่นด้วยเครื่องหมายจุลภาค) \
        ตัวอย่าง: True corp, AIS, SCB หรือ Data analyst, Data science, Data engineer",
        help="ตัวอย่าง: งาน A, งาน B, งาน C"
    )
    
    # Process input
    if choices_input:
        choice_names = [name.strip() for name in choices_input.split(",")]
        
        # Validate number of choices matches selected number
        if len(choice_names) != num_choices:
            st.error(f"กรุณาระบุชื่อให้ครบ {num_choices} อย่าง (พบ {len(choice_names)} อย่าง)")
            return
        
        # Validate that all choices have names
        if any(not name for name in choice_names):
            st.error("กรุณาระบุชื่อให้ครบทุกอย่าง")
            return
        
        # Display current choices
        st.write("สิ่งที่ต้องการเปรียบเทียบ:")
        for i, name in enumerate(choice_names, 1):
            st.write(f"{i}. {name}")
    
        tarot_data = gb.fetch_local_tarot_data()
        
        if st.button("ทำนายดวง"):
            st.write(" รอสักครู่ คำทำนายกำลังมา ...")
            if tarot_data is not None:
                cards, card_numbers = draw_comparison_spread(tarot_data, num_choices)
                
                if cards:
                    # Display spread
                    display_comparison_spread(cards, card_numbers, choice_names)
                    
                    # Display comparison reading
                    st.write("## การวิเคราะห์เปรียบเทียบ 🔮")
                    comparison = get_comparison_reading(cards, question_input, choice_names)
                    if comparison:
                        st.write(comparison)
                        predictions = {
                        "comparison_reading": comparison
                        }
                        # Save log
                        user_input = {
                            "num_choices": num_choices,
                            "choices": choice_names,
                            "question": question_input
                        }
                        
                        gb.save_reading_log(
                            user_input=user_input,
                            reading_type="comparison",
                            cards_drawn=cards,
                            predictions=predictions
                        )
                        gb.end_predict()
                        gb.survey()
    gb.button_under_page()

if __name__ == "__main__":
    main()
