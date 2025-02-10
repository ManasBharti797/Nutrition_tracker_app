import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import matplotlib.pyplot as plt
import re

# Load environment variables
load_dotenv()

# Configure Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Function to get response
def get_gemini_response(input_prompt, image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt, image[0]])
    return response.text

# Function to extract data
def extract_nutrition_data(response):
    nutrients = {"Carbs": 0, "Proteins": 0, "Fats": 0, "Sugar": 0}

    lines = response.split("\n")
    for line in lines:
        match = re.search(r"(\bCarbs\b|\bProteins\b|\bFats\b|\bSugar\b)\s*:\s*(\d+)", line)
        if match:
            key, value = match.groups()
            nutrients[key] = int(value)

    return nutrients

# Function to process uploaded image
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        # ✅ Resize image to 512x512 (Optimal for AI Processing)
        image = image.resize((512, 512))
        
        # ✅ Convert to RGB to avoid mode issues
        image = image.convert("RGB")
        
        bytes_data = uploaded_file.getvalue()
        image_parts = [{
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")


# 🏠 **Set Page Title & Sidebar**
st.set_page_config(page_title="Nutrition Tracker App", page_icon="🍎", layout="wide")

# 🎨 **Improved UI Styling**
st.markdown(
    """
    <style>
        .big-font { font-size:20px !important; }
        .stButton > button { background-color: #4CAF50; color: white; font-size:18px; }
    </style>
    """,
    unsafe_allow_html=True
)

# 📌 **Sidebar with Instructions**
st.sidebar.header("📌 How to Use")
st.sidebar.write("1️⃣ Upload an image of your food 🍔🥗\n")
st.sidebar.write("2️⃣ Click the 'Analyze' button 📊\n")
st.sidebar.write("3️⃣ Get detailed **nutritional information** 🔥💪")

# 🖼️ **Main App**
st.title("🍏 Nutrition Tracker App 🍽️")

# ✅ Corrected file uploader
uploaded_file = st.file_uploader(r"C:\Users\KIIT\Downloads\Food_img", type=["jpg", "jpeg", "png"])

# Display uploaded image
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

# ✅ Fix: Check if "results" exists in session_state BEFORE using it
if "results" not in st.session_state:
    st.session_state.results = []  # Initialize session state variable

# ✨ **Analyze Button**
if st.button("📊 Tell me about the Nutritional content!!"):
    progress_bar = st.progress(0)
    
    with st.spinner("Analyzing... Please wait ⏳"):
        progress_bar.progress(20)  
        image_data = input_image_setup(uploaded_file)

        progress_bar.progress(50)  
        response = get_gemini_response(
            "Analyze this food image and provide nutritional information.", image_data
        )

        progress_bar.progress(100)  
        
    # ✅ Append result to session_state
    st.session_state.results.append(response)  

    # ✅ Display results
    st.header("The Nutritional and Calorie contents are:")
    st.write(response)

    # ✅ Extract nutrition data
    nutrition_data = extract_nutrition_data(response)

    # Ensure no NaN values
    nutrition_data = {k: v if isinstance(v, (int, float)) and v > 0 else 1 for k, v in nutrition_data.items()}

    # ✅ Plot Pie Chart
    fig, ax = plt.subplots()
    ax.pie(nutrition_data.values(), labels=nutrition_data.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular
    st.pyplot(fig)
