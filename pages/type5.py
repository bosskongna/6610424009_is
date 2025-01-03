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
st.markdown("#### เพื่อตอบคำถามถึงความสัมพันธ์ระหว่างคุณ และบุคคลอีกบุคคล หรือความสัมพันธ์ของบุคคลที่ 2 และ 3")
st.write("ตัวอย่าง: คนชื่อ A รู้สึกยังไงกับเรา, คนชื่อแบงค์ รู้สึกยังไงกับ คนชื่อตาล")
gb.focus('')
TAROT_DATA_FILE = "/workspaces/6610424009_is/023_cleaned_all_tarot_card_data.csv"
st.error("คำเตือน: ไม่ควรถามคำถามเดิมซ้ำในช่วงเวลาเดียวกัน ควรเว้นระยะอย่างน้อย 2 อาทิตย์")

# Set Google Cloud credentials and project
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/workspaces/6610424009_is/mutelu-chat.json"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mutelu-chat"
vertexai.init(project="mutelu-chat", location="asia-southeast1")

def draw_relationship_spread(tarot_data):
    """Draw 6 unique cards for Relationship Spread positions"""
    try:
        total_cards = len(tarot_data)
        random_numbers = random.sample(range(1, total_cards + 1), 6)
        
        spread_positions = {
            'person1': None,     # First person's energy/feelings
            'person2': None,     # Second person's energy/feelings
            'dynamics': None,    # Current relationship dynamics
            'challenges': None,  # Challenges or obstacles
            'potential': None,   # Relationship potential
            'advice': None       # Guidance for the relationship
        }
        
        for position, num in zip(spread_positions.keys(), random_numbers):
            tarot_data_draw = tarot_data[tarot_data['card_no'] == num]
            if not tarot_data_draw.empty:
                spread_positions[position] = tarot_data_draw.iloc[0].to_dict()
        
        return spread_positions, random_numbers
    except Exception as e:
        st.error(f"Cannot draw cards: {e}")
        return None, None

import streamlit as st
import json
from vertexai.generative_models import GenerativeModel

def analyze_question_persons(question):
    try:
        model = GenerativeModel("gemini-1.5-flash-002")

        analysis_prompt = f"""
        Analyze this Thai relationship question: "{question}"

        Task: Identify two people in the relationship query.

        Rules:
        1. If question includes "เรา", "ฉัน", "ผม", "ดิฉัน": First person is "ผู้ถาม"
        2. Look for name after "คนชื่อ" and remove "คนชื่อ" prefix
        3. For "คนชื่อแดง รู้สึกยังไงกับเรา": person1="แดง", person2="ผู้ถาม"
        4. For "เรารู้สึกยังไงกับคนชื่อแดง": person1="ผู้ถาม", person2="แดง"
        5. For "คนชื่อแบงค์ รู้สึกยังไงกับ คนชื่อตาล": person1="แบงค์", person2="ตาล"

        Return EXACTLY (include quotes): {{"person1": "name1", "person2": "name2"}}

        Examples:
        Input: "คนชื่อแดง รู้สึกยังไงกับเรา" → {{"person1": "แดง", "person2": "ผู้ถาม"}}
        Input: "คนชื่อฟ้า รู้สึกยังไงกับเรา" → {{"person1": "ฟ้า", "person2": "ผู้ถาม"}}
        Input: "เรารู้สึกยังไงกับคนชื่อแดง" → {{"person1": "ผู้ถาม", "person2": "แดง"}}
        Input: "คนชื่อแดง รู้สึกยังไงกับ คนชื่อดำ" → {{"person1": "แดง", "person2": "ดำ"}}
        Input: "คนชื่อแบงค์ รู้สึกยังไงกับ คนชื่อตาล" → {{"person1": "แบงค์", "person2": "ตาล"}}
        """

        response = model.generate_content(analysis_prompt)

        # More Robust JSON Parsing:
        cleaned_response = response.text.strip()
        # Handle potential variations in spacing or extra characters
        start_index = cleaned_response.find('{')
        end_index = cleaned_response.rfind('}') + 1
        if start_index != -1 and end_index != -1:
              cleaned_response = cleaned_response[start_index:end_index]
        
        result = json.loads(cleaned_response)

        st.session_state['persons'] = result
        return result

    except Exception as e:
        print(f"Error during analysis: {e}")  # Log the error for debugging
        print(f"Problematic response: {response.text}")
        default_result = {"person1": "ผู้ถาม", "person2": "ผู้ที่ถูกถามถึง"}
        st.session_state['persons'] = default_result
        return default_result

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

def get_relationship_reading(question, card, position, sentiment,persons):
    try:
        model = GenerativeModel("gemini-1.5-flash-002")
        
        position_prompts = {
            'person1': f"""
            First Person Card:
            • Analyze current energy and feelings
            • Based on card: {card['title']}
            • Consider their perspective and emotions
            • Think about their current state of mind
            
            Response style:
            1. Must respond in Thai language
            2. Start with "สำหรับ{persons['person1']}..."
            3. Keep interpretation under 4 sentences
            4. Focus on emotional state and attitudes
            5. Use gentle and warm Thai language
            """,
            
            'person2': f"""
            Second Person Card:
            • Analyze their current energy and feelings
            • Based on card: {card['title']}
            • Consider their perspective and emotions
            • Think about their current state of mind
            
            Response style:
            1. Must respond in Thai language
            2. Start with "สำหรับ{persons['person2']}..."
            3. Keep interpretation under 4 sentences
            4. Focus on emotional state and attitudes
            5. Use gentle and warm Thai language
            """,
            
            'dynamics': f"""
            Current Dynamics Card:
            • Analyze the relationship's current state
            • Based on card: {card['title']}
            • Consider the interaction between both people
            • Look at the energy flow between them
            
            Response style:
            1. Must respond in Thai language
            2. Start with "ความสัมพันธ์ในปัจจุบัน..."
            3. Keep interpretation under 4 sentences
            4. Use gentle and warm Thai language
            """,
            
            'challenges': f"""
            Challenges Card:
            • Identify current or upcoming obstacles
            • Based on card: {card['title']}
            • Consider what needs attention
            • Think about potential difficulties
            
            Response style:
            1. Must respond in Thai language
            2. Start with "สิ่งที่ท้าทายในความสัมพันธ์..."
            3. Keep interpretation under 4 sentences
            4. Be honest but constructive in Thai
            """,
            
            'potential': f"""
            Potential Card:
            • Reveal the relationship's potential
            • Based on card: {card['title']}
            • Consider best possible outcomes
            • Look for positive opportunities
            
            Response style:
            1. Must respond in Thai language
            2. Start with "ศักยภาพของความสัมพันธ์..."
            3. Keep interpretation under 4 sentences
            4. Focus on positive possibilities in Thai
            """,
            
            'advice': f"""
            Advice Card:
            • Provide guidance for the relationship
            • Based on card: {card['title']}
            • Offer practical suggestions
            • Give hope and encouragement
            
            Response style:
            1. Must respond in Thai language
            2. Start with "คำแนะนำสำหรับความสัมพันธ์..."
            3. Keep advice clear and actionable
            4. End with encouragement in Thai
            """
        }
        
        base_prompt = """
        You are a skilled tarot reader providing insights in Thai language.
        Personality:
        • Use warm, gentle Thai language
        • Keep interpretations clear but meaningful
        • Balance honesty with encouragement
        • Be empathetic and supportive
        • Maintain a positive but realistic tone

        Important: While these instructions are in English, your response MUST be in Thai language  and no emoji..
        """
        
        full_prompt = base_prompt + position_prompts[position]
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        st.error(f"ไม่สามารถสร้างคำทำนายได้: {e}")
        return None
    
def get_relationship_summary(question, cards, sentiment):
    try:
        model = GenerativeModel("gemini-1.5-flash-002")
        
        summary_prompt = f"""
        Create a concise summary of this 6-card relationship spread reading in Thai.

        Question: {question}
        
        Cards:
        Person 1: {cards['person1']['title']}
        Person 2: {cards['person2']['title']}
        Dynamics: {cards['dynamics']['title']}
        Challenges: {cards['challenges']['title']}
        Potential: {cards['potential']['title']}
        Advice: {cards['advice']['title']}

        Guidelines:
        1. Only Thai language and a bit English - no other languages
        2. Start with "สรุปภาพรวมความสัมพันธ์..."
        3. Weave together insights from all 6 cards
        4. Address the dynamics between both people
        5. Provide constructive guidance
        6. End with hope and encouragement
        7. Keep to 5-6 sentences maximum
        
        Response format: Write a flowing paragraph, not bullet points.
        """

        response = model.generate_content(summary_prompt)
        return response.text

    except Exception as e:
        st.error(f"ไม่สามารถสร้างสรุปได้: {e}")
        return None
    
def display_relationship_spread(cards, card_numbers):
    # Get persons from global scope or pass as parameter if needed
    persons = st.session_state.get('persons', {"person1": "ผู้ถาม", "person2": "ผู้ที่ถูกถามถึง"})
    
    # First row - The two people
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"### {persons['person1']}")
        st.write(f"**{cards['person1']['title']}**")
        image_path = f"assets/card_{card_numbers[0]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
            
    with col2:
        st.write(f"### {persons['person2']}")
        st.write(f"**{cards['person2']['title']}**")
        image_path = f"assets/card_{card_numbers[1]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
    
    
    # Second row - Dynamics and Challenges
    col1, col2 = st.columns(2)
    with col1:
        st.write("### ความสัมพันธ์ปัจจุบัน")
        st.write(f"**{cards['dynamics']['title']}**")
        image_path = f"assets/card_{card_numbers[2]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
            
    with col2:
        st.write("### ความท้าทาย")
        st.write(f"**{cards['challenges']['title']}**")
        image_path = f"assets/card_{card_numbers[3]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
    
    # Third row - Potential and Advice
    col1, col2 = st.columns(2)
    with col1:
        st.write("### ศักยภาพของความสัมพันธ์")
        st.write(f"**{cards['potential']['title']}**")
        image_path = f"assets/card_{card_numbers[4]}.png"
        if os.path.exists(image_path):
            st.image(image_path)
            
    with col2:
        st.write("### คำแนะนำ")
        st.write(f"**{cards['advice']['title']}**")
        image_path = f"assets/card_{card_numbers[5]}.png"
        if os.path.exists(image_path):
            st.image(image_path)

def main():
    user_question = st.text_input("โปรดใส่คำถามของคุณ:")
    
    # Add spread type selection
    spread_type = "Relationship Spread (6 ใบ)"
    
    tarot_data = gb.fetch_local_tarot_data()
    
    if st.button("ทำนายดวง") and user_question:
        st.write(" รอสักครู่ คำทำนายกำลังมา ...")
        if tarot_data is not None:
            sentiment = analyze_sentiment(user_question)
            category = get_question_category(user_question)
            
            # Analyze persons in the question first
            # In main function
            persons = analyze_question_persons(user_question)
            st.session_state['persons'] = persons
            cards, card_numbers = draw_relationship_spread(tarot_data)
            
            if cards:
                # Display relationship spread layout with only cards and card_numbers
                display_relationship_spread(cards, card_numbers)
                
                # Display reading
                st.markdown("---")
                st.write("## การทำนาย 🔮")
                predictions = {}
                
                positions = ['person1', 'person2', 'dynamics', 'challenges', 'potential', 'advice']
                for position in positions:
                    prediction = get_relationship_reading(
                        user_question,
                        cards[position],
                        position,
                        sentiment,
                        persons  # Pass persons information
                    )
                    if prediction:
                        st.write(prediction)
                        predictions[position] = prediction
                        if position != 'advice':
                            st.markdown("---")
                try:
                    st.markdown("---")
                    st.write("## สรุปภาพรวมความสัมพันธ์ 🎴")
                    summary = get_relationship_summary(
                        user_question,
                        cards,
                        sentiment
                    )
                    if summary:
                        st.write(summary)
                        predictions['summary'] = summary
                except Exception as e:
                    st.error("ไม่สามารถสร้างสรุปได้ กรุณาลองกดปุ่มทำนายดวงอีกครั้ง")
        
                user_input = {
                    "question": user_question,
                    "sentiment": sentiment,
                    "persons": persons
                }
                
                gb.save_reading_log(
                    user_input=user_input,
                    reading_type="relationship",
                    cards_drawn=cards,
                    predictions=predictions
                )
                gb.end_predict()
                gb.survey()
    gb.button_under_page()

if __name__ == "__main__":
    main()