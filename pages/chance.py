import streamlit as st
import pandas as pd
import random
import vertexai
from vertexai.preview.generative_models import GenerativeModel
import global_set as gb
import os

gb.logo()

if st.button("ย้อนกลับ"):
    st.switch_page("/workspaces/6610424009_is/pages/streamlit_app.py")

st.title("เปิดไพ่เพื่อตอบคำถาม ใช่/ไม่ใช่ หรือโอกาสที่จะเกิด (คำถามปลายปิด)")
st.write("ตัวอย่าง: ปีนี้มีโอกาสย้ายงานหรือไม่, ปีนี้จะได้เลื่อนตำแหน่งหรือไม่, คนรักยังรักเราอยู่ไหม ?")
gb.ohm()
st.error("คำเตือน: ไม่ควรถามคำถามเดิมซ้ำในข่วงเวลา 1 เดือน")
gb.focus()
gb.survey()
TAROT_DATA_FILE = "/workspaces/6610424009_is/cards/023_cleaned_all_tarot_card_data.csv"

# Set Google Cloud credentials and project
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/workspaces/6610424009_is/mutelu-chat.json"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mutelu-chat"
vertexai.init(project="mutelu-chat", location="asia-southeast1")

def analyze_sentiment(text):
    """Analyze the sentiment of user's question with detailed Thai context."""
    try:
        model = GenerativeModel("gemini-pro")
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

def get_ai_response(question, card, sentiment):
    """Get AI response using Gemini in Thai."""
    try:
        model = GenerativeModel("gemini-pro")
        
        chance = float(card['chance'])
        if sentiment == "NEGATIVE":
            chance = 100 - chance
            
        full_prompt = f"""
        You are a highly experienced tarot card reader with over 20 years of expertise in tarot reading and interpretation.

        Your Personality:
        • You speak in a polite, gentle, and approachable manner.
        • You use language that is simple yet profound.
        • You offer constructive and encouraging guidance.
        • You demonstrate kindness and genuine care for those seeking your advice.

        Context:
        - User's Question: {question}
        - Card Drawn: {card['title']}
        - Chance of Occurrence: {chance}%
        - Additional Notes: {card['chance_note']}

        Please provide a Thai language reading that only following:
        1. Repeat the question
        END
        """
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        st.error(f"ไม่สามารถสร้างคำทำนายได้: {e}")
        return None

# def fetch_local_tarot_data(file_path):
#     try:
#         df = pd.read_csv(file_path)
#         return df
#     except Exception as e:
#         st.error(f"ไม่สามารถโหลดข้อมูลไพ่ทาโรต์ได้: {e}")
#         return None

def draw_random_card(tarot_data):
    try:
        random_number = random.randint(1, len(tarot_data))
        tarot_data_draw = tarot_data[tarot_data['card_no'] == random_number]
        card = tarot_data_draw.iloc[0]
        return card.to_dict(), random_number
    except Exception as e:
        st.error(f"ไม่สามารถสุ่มไพ่ได้: {e}")
        return None, None

def main():
    # Text input for user's question
    user_question = st.text_input("โปรดใส่คำถามของคุณ:")
    
    # Fetch Tarot Data from local file
    tarot_data = gb.fetch_local_tarot_data()
    
    # if user_question:
        # st.success("ตั้งสมาธิ หายใจเข้าลึกๆ แล้วกดปุ่ม ทำนายดวง")
    
    if st.button("ทำนายดวง") and user_question:
        if tarot_data is not None:
            # Analyze sentiment
            sentiment = analyze_sentiment(user_question)
            
            # Draw a random card
            card, rndm_num = draw_random_card(tarot_data)
            
            if card:
                # Display card details
                st.write("### ไพ่ของคุณ")
                st.write(f"**ชื่อไพ่:** {card['title']}")
                
                # Display card image
                image_path = f"assets/card_{rndm_num}.png"
                if os.path.exists(image_path):
                    st.image(image_path, width=300)
                else:
                    st.write("ไม่สามารถแสดงภาพไพ่ได้")
                
                # Generate and display prediction
                st.write("รอสักครู่ คำทำนายกำลังมา ...")
                
                ai_response = get_ai_response(user_question, card, sentiment)
                if ai_response:
                    st.write("### คำทำนาย")
                    st.write(ai_response)
                    
                    # Display chance percentage
                    chance = float(card['chance'])
                    if sentiment == "NEGATIVE":
                        chance = 100 - chance
                    st.write(f"**โอกาสความเป็นไปได้:** {chance}%")
                else:
                    st.error("ไม่สามารถสร้างคำทำนายได้")
            else:
                st.error("ไม่สามารถสุ่มไพ่ได้")

if __name__ == "__main__":
    main()