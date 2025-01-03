import streamlit as st
import pandas as pd
import random
import vertexai
from vertexai.preview.generative_models import GenerativeModel
import global_set as gb
import os

gb.logo()
gb.initialize_vertexai()  # Initialize Vertex
bucket = gb.initialize_gcs()  # Initialize GC AI


gb.button_main_page()

st.write("### ตอบคำถามต่างๆ (คำถามปลายเปิด)")
st.write("ตัวอย่าง: งานปีนี้จะเป็นยังไงบ้าง, สุขภาพปีนี้เป็นยังไงบ้าง, อีก 3 เดือน การเงินจะเป็นยังไง")
gb.focus('')
TAROT_DATA_FILE = "/workspaces/6610424009_is/023_cleaned_all_tarot_card_data.csv"

st.error("คำเตือน: ไม่ควรถามคำถามเดิมในช่วงเวลาเดียวกัน")

# Set Google Cloud credentials and project

def draw_random_card(tarot_data):
    """Draw 3 unique random cards from the deck"""
    try:
        # Get total number of cards
        total_cards = len(tarot_data)
        
        # Generate 3 unique random numbers
        random_numbers = random.sample(range(1, total_cards + 1), 3)
        
        # Get the cards for these numbers
        cards = []
        card_numbers = []
        for num in random_numbers:
            tarot_data_draw = tarot_data[tarot_data['card_no'] == num]
            if not tarot_data_draw.empty:
                cards.append(tarot_data_draw.iloc[0].to_dict())
                card_numbers.append(num)
            
        return cards, card_numbers
    except Exception as e:
        st.error(f"ไม่สามารถสุ่มไพ่ได้: {e}")
        return None, None


def analyze_sentiment(text):
    """Analyze the sentiment of user's question with detailed Thai context."""
    try:
        model = GenerativeModel("gemini-1.5-flash-002")
        sentiment_prompt = f"""
        As a sentiment analyzer, evaluate the following question in Thai context.
        
        Guidelines for analysis:
        - POSITIVE: Questions about hopes, dreams, success, love, opportunities
          Example: "ฉันจะได้เลื่อนตำแหน่งไหม" "จะได้แต่งงานในปีนี้ไหม" "จะได้งานใหม่ไหม"
        
        - NEUTRAL: General questions seeking information without strong emotion
          Example: "ปีนี้จะได้ย้ายบ้านไหม" "จะได้เดินทางในปีนี้ไหม" "จะได้เปลี่ยนงานไหม"
        
        - NEGATIVE: Questions expressing worry, doubt, fear, or negative expectations
          Example: "เขาจะเลิกกับฉันไหม" "จะโดนไล่ออกจากงานไหม" "จะเป็นหนี้ไหม"

        Question to analyze: {text}
        
        Important:
        - Focus on the emotional undertone and context of the question
        - Consider Thai cultural nuances
        - Look for keywords indicating hope vs worry
        _ No need emoji
        
        Respond with only one word: POSITIVE, NEUTRAL, or NEGATIVE
        """
        
        response = model.generate_content(sentiment_prompt)
        sentiment = response.text.strip().upper()
        
        # Validate response
        valid_sentiments = ["POSITIVE", "NEUTRAL", "NEGATIVE"]
        if sentiment not in valid_sentiments:
            return "NEUTRAL"
            
        return sentiment
        
    except Exception as e:
        st.error(f"ไม่สามารถวิเคราะห์ความรู้สึกได้: {e}")
        return "NEUTRAL"  # Default to neutral if analysis fails
def get_question_category(question):
    """Determine the category of the user's question"""
    try:
        model = GenerativeModel("gemini-1.5-flash-002")
        category_prompt = f"""
        Analyze this question in Thai and determine its category. Question: {question}
        
        Categories:
        - LOVE: relationships, marriage, romance
        - WORK: career, business, education
        - MONEY: finances, investments, wealth
        - HEALTH: physical health, mental health, wellness
        - TRAVEL: journeys, moving, relocation
        
        Response format: Return only one word - LOVE, WORK, MONEY, HEALTH, or TRAVEL
        """
        response = model.generate_content(category_prompt)
        category = response.text.strip().upper()
        
        valid_categories = ["LOVE", "WORK", "MONEY", "HEALTH", "TRAVEL"]
        return category if category in valid_categories else "GENERAL"
    except Exception as e:
        st.error(f"Error determining question category: {e}")
        return "GENERAL"

def get_ai_response(question, card, position, category, sentiment):
    """Get AI response using Gemini with improved prompting"""
    try:
        model = GenerativeModel("gemini-1.5-flash-002")
        
        # Get the relevant advice based on category
        category_advice = card[category.lower()] if category != "GENERAL" else card['general']
        
        # Base personality and context
        base_prompt = """
        You are a highly experienced tarot reader with deep knowledge of card interpretation.
        Personality traits:
        • Speak gently and warmly in Thai language
        • Use clear, simple yet meaningful language
        • Offer guidance with empathy and wisdom
        • Balance honesty with encouragement
        • Keep responses concise but insightful
        • do not put "ไพ่กลับหัว" in response
        • No emoji
        """
        
        # Position-specific prompts
        position_prompts = {
            1: f"""
            First Card - Present Situation:
            • Analyze the current energies around: {question}
            • Focus on the immediate situation
            • Interpret this card: {card['title']}
            • Use this card's wisdom for {category}: {category_advice}
            • Connect the interpretation to the querent's question
            
            Response style:
            1. Start with "ไพ่ใบแรกสะท้อนสถานการณ์ปัจจุบันของคุณ..."
            2. Keep the interpretation under 4 sentences
            3. Be specific to the question context
            """,
            
            2: f"""
            Second Card - Challenges:
            • Reveal potential obstacles regarding: {question}
            • Based on card: {card['title']}
            • Consider this specific guidance: {category_advice}
            • If sentiment is negative, focus on cautions
            • If sentiment is positive, focus on opportunities
            
            Response style:
            1. Start with "ไพ่ใบที่สองแสดงให้เห็นสิ่งที่ต้องระวัง..."
            2. This position mean reverse card but do not put "ไพ่กลับหัว" in response
            3. Keep the interpretation under 4 sentences
            4. Include practical insights
            """,
            
            3: f"""
            Third Card - Advice:
            • Provide guidance for: {question}
            • Based on card: {card['title']}
            • Include this suggestion: {card['suggestion']}
            • Offer practical, actionable advice
            • End with hope and encouragement
            
            Response style:
            1. Start with "ไพ่ใบสุดท้ายให้คำแนะนำว่า..."
            2. Keep the advice clear and actionable
            3. End with a positive note
            """
        }
        
        # Combine prompts
        full_prompt = base_prompt + position_prompts[position]
        
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        st.error(f"ไม่สามารถสร้างคำทำนายได้: {e}")
        return None

def main():
    user_question = st.text_input("โปรดใส่คำถามของคุณ:")
    
    tarot_data = gb.fetch_local_tarot_data()
    
    if st.button("ทำนายดวง") and user_question:
        st.write(" รอสักครู่ คำทำนายกำลังมา ...")
        if tarot_data is not None:
            sentiment = analyze_sentiment(user_question)
            category = get_question_category(user_question)
            cards, card_numbers = draw_random_card(tarot_data)
            
            if cards:
                # Display cards in row (keep your existing display code)
                cols = st.columns(3)
                for i, (card, rndm_num) in enumerate(zip(cards, card_numbers)):
                    with cols[i]:
                        st.write(f"### ไพ่ที่ {i+1}")
                        st.write(f"**{card['title']}**")
                        image_path = f"assets/card_{rndm_num}.png"
                        if os.path.exists(image_path):
                            st.image(image_path)
                
                # Display reading and store predictions
                st.markdown("---")
                st.write("## การทำนาย 🔮")
                predictions = {}  # Store all predictions
                
                for i, (card, _) in enumerate(zip(cards, card_numbers), 1):
                    prediction = get_ai_response(
                        user_question, 
                        card, 
                        i, 
                        category, 
                        sentiment
                    )
                    if prediction:
                        st.write(prediction)
                        predictions[f"card_{i}"] = prediction  # Store prediction
                        if i < 3:
                            st.markdown("---")
                
                # Save reading log
                user_input = {
                    "question": user_question,
                    "sentiment": sentiment,
                    "category": category
                }
                
                cards_data = []  # Prepare cards data
                for card, card_num in zip(cards, card_numbers):
                    cards_data.append({
                        "title": card['title'],
                        "card_no": card_num
                    })
                
                gb.save_reading_log(
                    user_input=user_input,
                    reading_type="three_card",
                    cards_drawn=cards_data,
                    predictions=predictions
                )
                            
                gb.end_predict()
                gb.survey()

    gb.button_under_page()

if __name__ == "__main__":
    main()