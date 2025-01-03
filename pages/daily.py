
import streamlit as st
import pandas as pd
import random
import vertexai
from vertexai.preview.generative_models import GenerativeModel
import global_set as gb
import os
import datetime


gb.logo()

gb.button_main_page()

st.markdown("### คำทำนายรายวัน")
gb.focus('no input')
st.error("คำเตือน: การดูดวงรายวัน ควรดูแค่วันละ 1 ครั้ง")
TAROT_DATA_FILE = "/workspaces/6610424009_is/cards/023_cleaned_all_tarot_card_data.csv"

# Set Google Cloud credentials and projectS
# gb.initialize_vertexai()  # Initialize Vertex

# bucket, services_initialized = gb.initialize_services()
# gb.api_key()


# Initialize Vertex AI with project and location

# # Fetch tarot data from local CSV
# def fetch_local_tarot_data(file_path):
#     """Fetch tarot data from local CSV file."""
#     try:
#         df = pd.read_csv(file_path)
#         return df
#     except Exception as e:
#         st.error(f"ไม่สามารถโหลดข้อมูลไพ่ทาโรต์ได้: {e}")
#         return None

# Generate AI interpretation using Gemini
def get_ai_response(prompt):
    """Get AI response using Gemini in Thai."""
    try:
        # Remove vertexai.init() from here since we initialized it at the top
        motdel = GenerativeModel("gemini-1.5-flash-002")
        full_prompt = f"""
        You are a highly experienced tarot card reader with over 20 years of expertise in tarot reading and interpretation.

	    Your Personality:
		•	You speak in a polite, gentle, and approachable manner.
	    •	You use language that is simple yet profound.
	    •	You offer constructive and encouraging guidance.
	    •	You demonstrate kindness and genuine care for those seeking your advice.

	    Reading Style:
		1.	Explain the meaning of the drawn card.
	    2.	Interpret its relevance to the seeker’s current situation.
	    3.	Provide actionable and practical advice based on the card’s insights.
        4.  Not too long message

	    Respond clearly, concisely, with empathy and no need to introduce your self.

        {prompt}
        
        """
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        st.error(f"ไม่สามารถสร้างคำทำนายได้: {e}")
        return None
def translate_to_thai(text):
    """Translate text to Thai using Gemini."""
    try:
        model = GenerativeModel("gemini-1.5-flash-002")
        translation_prompt = f"""
        Please translate the following text to Thai. 
        Maintain the meaning and tone while making it sound natural in Thai:

        {text}

        Translate to Thai:
        """
        response = model.generate_content(translation_prompt)
        return response.text
    except Exception as e:
        st.error(f"ไม่สามารถแปลข้อความได้: {e}")
        return None

# In your main function, modify the AI response handling:


# Tarot card randomization
def draw_random_card(tarot_data):
    """Draw a random card from the tarot dataset."""
    try:
        random_number = random.randint(1, len(tarot_data))
        tarot_data_draw = tarot_data[tarot_data['card_no'] == random_number]
        card = tarot_data_draw.iloc[0]
        return card.to_dict(),random_number
    except Exception as e:
        st.error(f"ไม่สามารถสุ่มไพ่ได้: {e}")
        return None

# Streamlit App
def main():

    # Fetch Tarot Data from local file
    tarot_data = gb.fetch_local_tarot_data()
    
    if st.button("ทำนายดวง"):
        if tarot_data is not None:
            # Draw a random card
            card, rndm_num = draw_random_card(tarot_data)
            
            if card:
                # Display card details
                st.write("### ไพ่ของคุณ")
                st.write(f"**ชื่อไพ่:** {card['title']}")
                cards_data = {
                    "daily": {
                        "title": card["title"],
                        "card_no": card["card_no"]
                        # Include other card data if needed
                    }
                }
                # st.write(f"**หมายเลขไพ่:** {card['card_no']}")
                image_path = f"assets/card_{rndm_num}.png"
                if os.path.exists(image_path):
                    st.image(image_path, width=300)
                else:
                    st.write("ไม่สามารถแสดงภาพไพ่ได้")
                # Generate AI interpretation
                st.write(" รอสักครู่ คำทำนายกำลังมา ...")
                prompt = f"""
                This tarot reading is to understand the overall outlook for today and identify any areas of caution.
                Please interpret the card {card['title']} and predict what is likely to happen today, based on the information provided: {card['content']}.
                """
                
                ai_response = get_ai_response(prompt)
                
                if ai_response:
                    thai_response = translate_to_thai(ai_response)
                    if thai_response:
                        st.write("### คำทำนาย")
                        st.write(thai_response)
                        # Save log
                        # Structure predictions
                        predictions = {
                            "daily_prediction": thai_response
                        }
                        
                        # Structure user input
                        user_input = {
                            "type": "daily_reading",
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                                
                        gb.save_reading_log(
                            user_input=user_input,
                            reading_type="daily",
                            cards_drawn=cards_data,
                            predictions=predictions
                        )
                        gb.end_predict()
                        gb.survey()
                    else:
                        st.error("ไม่สามารถแปลคำทำนายได้")
                else:
                    st.error("ไม่สามารถสร้างคำทำนายได้")
            else:
                st.error("ไม่สามารถสุ่มไพ่ได้")
        else:
            st.error("ไม่สามารถโหลดข้อมูลไพ่ได้")
    gb.button_under_page()

# Run the main function
if __name__ == "__main__":
    main()