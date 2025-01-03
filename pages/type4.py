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

st.markdown("#### เพื่อตอบคำถามต่างๆ (คำถามปลายเปิด) ละเอียดกว่าการเปิดไพ่ 3 ใบ")
st.write("ตัวอย่าง: งานปีนี้จะเป็นยังไงบ้าง, สุขภาพปีนี้เป็นยังไงบ้าง, ควรรับงานนี้ไหม")
gb.focus('')
TAROT_DATA_FILE = "/workspaces/6610424009_is/023_cleaned_all_tarot_card_data.csv"

st.error("คำเตือน: ไม่ควรถามคำถามเดิมในช่วงเวลาเดียวกัน")

# Set Google Cloud credentials and project
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/workspaces/6610424009_is/mutelu-chat.json"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mutelu-chat"
vertexai.init(project="mutelu-chat", location="asia-southeast1")

def draw_cross_spread_cards(tarot_data):
    """Draw 5 unique random cards for Cross Spread positions"""
    try:
        # Get total number of cards
        total_cards = len(tarot_data)
        
        # Generate 5 unique random numbers
        random_numbers = random.sample(range(1, total_cards + 1), 5)
        
        # Create a dictionary to store cards by position
        spread_positions = {
            'center': None,  # Card 4 (Center position)
            'left': None,    # Card 1 (Left position)
            'right': None,   # Card 3 (Right position)
            'top': None,     # Card 2 (Top position)
            'bottom': None   # Card 5 (Bottom position)
        }
        
        # Assign cards to positions
        for position, num in zip(spread_positions.keys(), random_numbers):
            tarot_data_draw = tarot_data[tarot_data['card_no'] == num]
            if not tarot_data_draw.empty:
                spread_positions[position] = tarot_data_draw.iloc[0].to_dict()
        
        return spread_positions, random_numbers
    except Exception as e:
        st.error(f"Cannot draw cards: {e}")
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
        
        # Get the relevant advice based on category, with error handling
        category_advice = card.get(category.lower(), card.get('general', ''))
        
        # Base personality and context
        base_prompt = """
        You are a highly experienced tarot reader with deep knowledge of card interpretation.
        Personality traits:
        • Speak gently and warmly in Thai language
        • Use clear, simple yet meaningful language
        • Offer guidance with empathy and wisdom
        • Balance honesty with encouragement
        • Keep responses concise but insightful
        """
        
        # Position-specific prompts without relying on keywords
        position_prompts = {
            1: f"""
            Center Card - Present Situation:
            • Analyze the current energies around: {question}
            • Focus on the immediate situation
            • Interpret this card: {card['title']}
            • Connect the interpretation to the querent's question
            
            Response style:
            1. Start with "ไพ่ตรงกลางสะท้อนสถานการณ์ปัจจุบันของคุณ..."
            2. Keep the interpretation under 4 sentences
            3. Be specific to the question context
            """,
            
            2: f"""
            Left Card - Past Influences:
            • Analyze past influences regarding: {question}
            • Based on card: {card['title']}
            • Connect past experiences to present situation
            
            Response style:
            1. Start with "ไพ่ด้านซ้ายแสดงถึงอดีตที่ผ่านมา..."
            2. Keep the interpretation under 4 sentences
            3. Include practical insights
            """,
            
            3: f"""
            Right Card - Future Influences:
            • Analyze future potential regarding: {question}
            • Based on card: {card['title']}
            • Focus on upcoming opportunities or challenges
            
            Response style:
            1. Start with "ไพ่ด้านขวาชี้ให้เห็นแนวโน้มในอนาคต..."
            2. Keep the interpretation under 4 sentences
            3. Be encouraging but realistic
            """,
            
            4: f"""
            Top Card - Goals/Aspirations:
            • Analyze highest potential regarding: {question}
            • Based on card: {card['title']}
            • Focus on achievable goals
            
            Response style:
            1. Start with "ไพ่ด้านบนแสดงถึงเป้าหมายที่เป็นไปได้..."
            2. Keep the interpretation under 4 sentences
            3. End with encouragement
            """,
            
            5: f"""
            Bottom Card - Foundation:
            • Analyze underlying influences regarding: {question}
            • Based on card: {card['title']}
            • Reveal deeper insights and root causes
            
            Response style:
            1. Start with "ไพ่ด้านล่างเผยให้เห็นรากฐานที่ซ่อนอยู่..."
            2. Keep the interpretation under 4 sentences
            3. Connect to overall reading
            """
        }
        
        # Get position prompt with fallback
        position_prompt = position_prompts.get(position, position_prompts[1])
        
        # Combine prompts
        full_prompt = base_prompt + position_prompt
        
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        st.error(f"ไม่สามารถสร้างคำทำนายได้: {e}")
        return None

def get_overall_summary(question, cards, category, sentiment):
    """Generate an overall summary of the cross spread reading"""
    try:
        model = GenerativeModel("gemini-1.5-flash-002")
        
        summary_prompt = f"""
        As an experienced tarot reader, create a concise overall summary of this 5-card cross spread reading in Thai language.

        Question: {question}
        Category: {category}
        Sentiment: {sentiment}

        Cards in position:
        Center (Present): {cards['center']['title']}
        Left (Past): {cards['left']['title']}
        Right (Future): {cards['right']['title']}
        Top (Goals): {cards['top']['title']}
        Bottom (Foundation): {cards['bottom']['title']}

        Guidelines:
        1. Start with "สรุปภาพรวมจากไพ่ทั้ง 5 ใบ..."
        2. Weave together the story from all 5 cards
        3. Focus on answering the querent's question
        4. Provide practical guidance
        5. End with hope and encouragement
        6. Keep the summary to 4-5 sentences maximum
        7. Use warm and empathetic tone

        Response format: Write a flowing paragraph, not bullet points.
        """

        response = model.generate_content(summary_prompt)
        return response.text

    except Exception as e:
        st.error(f"ไม่สามารถสร้างสรุปได้: {e}")
        return None

def main():
    user_question = st.text_input("โปรดใส่คำถามของคุณ:")
    
    tarot_data = gb.fetch_local_tarot_data()
    
    if st.button("ทำนายดวง") and user_question:
        st.write(" รอสักครู่ คำทำนายกำลังมา ...")
        if tarot_data is not None:
            sentiment = analyze_sentiment(user_question)
            category = get_question_category(user_question)
            cards, card_numbers = draw_cross_spread_cards(tarot_data)
            
            if cards:
                # Create layout for cross spread
                col1, col2, col3 = st.columns(3)
                
                # Top card
                with col2:
                    st.write("### ไพ่ด้านบน")
                    st.write(f"**{cards['top']['title']}**")
                    image_path = f"assets/card_{card_numbers[3]}.png"
                    if os.path.exists(image_path):
                        st.image(image_path)
                
                # Middle row (Left, Center, Right)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("### ไพ่ด้านซ้าย")
                    st.write(f"**{cards['left']['title']}**")
                    image_path = f"assets/card_{card_numbers[1]}.png"
                    if os.path.exists(image_path):
                        st.image(image_path)
                
                with col2:
                    st.write("### ไพ่ตรงกลาง")
                    st.write(f"**{cards['center']['title']}**")
                    image_path = f"assets/card_{card_numbers[0]}.png"
                    if os.path.exists(image_path):
                        st.image(image_path)
                
                with col3:
                    st.write("### ไพ่ด้านขวา")
                    st.write(f"**{cards['right']['title']}**")
                    image_path = f"assets/card_{card_numbers[2]}.png"
                    if os.path.exists(image_path):
                        st.image(image_path)
                
                # Bottom card
                col1, col2, col3 = st.columns(3)
                with col2:
                    st.write("### ไพ่ด้านล่าง")
                    st.write(f"**{cards['bottom']['title']}**")
                    image_path = f"assets/card_{card_numbers[4]}.png"
                    if os.path.exists(image_path):
                        st.image(image_path)
                
                # Display reading
                st.markdown("---")
                st.write("## การทำนาย 🔮")

                predictions = {}
                # Process cards in the correct order: center, left, right, top, bottom
                positions = ['center', 'left', 'right', 'top', 'bottom']
                for i, position in enumerate(positions, 1):
                    prediction = get_ai_response(
                        user_question, 
                        cards[position], 
                        i,  # Position number 1-5
                        category, 
                        sentiment
                    )
                    if prediction:
                        st.write(prediction)
                        predictions[position] = prediction
                        if i < 5:
                            st.markdown("---")
                # Add this after the individual card readings:
                st.markdown("---")
                st.write("## สรุปภาพรวม 🎴")
                summary = get_overall_summary(
                    user_question,
                    cards,
                    category,
                    sentiment
                )
                if summary:
                    st.write(summary)
                
                # Save reading log
                user_input = {
                    "question": user_question,
                    "sentiment": sentiment,
                    "category": category
                }
                
                gb.save_reading_log(
                    user_input=user_input,
                    reading_type="cross_spread",
                    cards_drawn=cards,
                    predictions=predictions
                )
                gb.end_predict()
                gb.survey()
    gb.button_under_page()

if __name__ == "__main__":
    main()