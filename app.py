import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Setup Streamlit page
st.set_page_config(page_title="Election Assistant Pro", page_icon="🗳️", layout="wide")

# Mock data for Contextual Logic
states_cities = {
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Noida"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"],
    "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru", "Hubli"],
    "Delhi": ["New Delhi", "North Delhi", "South Delhi"]
}

# --- 1. Security Check (Hackathon Compliance) ---
# Dummy API key check for Security
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.sidebar.warning("⚠️ GOOGLE_API_KEY not found in environment variables. Set it for the AI Assistant to work.", icon="⚠️")
else:
    # Initialize genai if key exists
    genai.configure(api_key=api_key)

# Initialize Gemini Model functionality
def get_gemini_response(prompt, context):
    if not api_key:
        return "System Warning: Google API Key is missing. Please set your GOOGLE_API_KEY environment variable. Let me know if you have other questions!"
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        # Instruct the model to utilize context contextually
        system_instruction = f"You are a helpful and factual Election Assistant in India. Keep answers concise. Context: User is from {context['city']}, {context['state']}, age {context['age']}."
        full_prompt = f"System: {system_instruction}\nUser: {prompt}\nAssistant:"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to Gemini API: {e}"

# --- 2. Contextual Logic via Sidebar ---
st.sidebar.title("👤 Voter Profile")

# State Selection
selected_state = st.sidebar.selectbox(
    "Select your State", 
    options=list(states_cities.keys()),
    help="Choose the state where you are registered to vote or currently reside."
)

# City Selection
selected_city = st.sidebar.selectbox(
    "Select your City", 
    options=states_cities[selected_state],
    help="Choose your city to get localized information on polling booths."
)

# Age Selection
age = st.sidebar.number_input(
    "Enter your Age", 
    min_value=1, 
    max_value=120, 
    value=18, 
    step=1,
    help="Enter your current age in years. The eligible voting age in India is 18."
)

context = {
    "state": selected_state,
    "city": selected_city,
    "age": age
}

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Keep your Voter ID (EPIC) ready before heading to the polling station.")

# --- 3. Main Dashboard & Interactive Timeline ---
st.title("🗳️ Election Process & Timeline Assistant")
st.subheader(f"Your personalized election guide for {selected_city}, {selected_state}.")

# Contextual Eligibility Logic
if age < 18:
    st.error("🚫 **Not Eligible.** You must be at least 18 years old to vote in India. Keep learning about the democratic process so you are ready when you turn 18!", icon="🚫")
    st.info(f"You will become eligible to vote in {(18 - age)} year(s).")
    
else:
    if age == 18:
        st.success("🎉 **Welcome First Time Voter!** We have highlighted the initial registration steps for you below.", icon="🎉")
    else:
        st.success("✅ **You are eligible to vote.** Please follow the timeline below to ensure a smooth voting experience.", icon="✅")

    st.markdown("---")
    st.markdown("### 🗺️ Your Voting Journey Timeline")

    # Using columns to create a horizontal timeline feel
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if age == 18:
            st.info("**1. Registration (CRITICAL)**\n\nApply for a new Voter ID (Form 6) via NVSP portal or Voter Helpline App.")
        else:
            st.info("**1. Registration Check**\n\nEnsure your name is present in the Electoral Roll. Apply for corrections if any.")
            
    with col2:
        st.warning("**2. Booth Slip**\n\nDownload your informational Booth Slip 1-2 weeks prior to polling day.")
        
    with col3:
        st.success("**3. Polling Day**\n\nVisit your assigned polling station with your Voter ID to cast your vote.")
        
    with col4:
        st.error("**4. Counting**\n\nFollow official ECI channels on counting day to see the election results.")

    st.write("")
    st.write("#### Detailed Steps")

    # More interactive view using expanders to dive into the pipeline
    with st.expander("📝 1. Registration Details", expanded=(age==18)):
        st.markdown(f"""
        **How to Register (Form 6) from {selected_state}:**
        - Visit the [National Voters' Service Portal (NVSP)](https://www.nvsp.in/) or download the Voter Helpline App.
        - Log in or create an account.
        - Fill out 'Form 6' for new voter registration.
        - Upload a recent passport photo, age proof, and address proof.
        """)
        st.button("Go to NVSP portal", help="Click to open the external NVSP portal in a new tab.", disabled=True)

    with st.expander("📄 2. Voter Information Slip (VIS)"):
        st.markdown("""
        **What is it?**
        Your VIS contains details like your Polling Booth Name, Date, and Time of the election, and your Serial Number on the Electoral Roll. 
        It is distributed by Election Officials but can also be downloaded digitally.
        """)
        st.button("Download Booth Slip Guide", help="Click to view details on how to download your slip online.", disabled=True)

    with st.expander("🗳️ 3. Polling Day Protocol"):
        st.markdown(f"""
        **When you arrive at the booth in {selected_city}:**
        1. **First Polling Officer:** Checks your name on the list and verifies your ID (like Voter ID/Aadhaar).
        2. **Second Polling Officer:** Inks your left forefinger, gives you a slip, and takes your signature/thumbprint in the register.
        3. **Third Polling Officer:** Takes the printed slip from you and checks the ink before allowing you in.
        4. **Voting Compartment:** Press the blue button against the candidate of your choice on the EVM. Wait for the beep sound indicating success. Note the VVPAT slip printed.
        """)

    with st.expander("📊 4. Results & Counting"):
        st.markdown("""
        **Tracking Results:**
        Counting is conducted under strict security with EVMs brought from strong rooms. Results are streamed live on the ECI Election Trends portal.
        """)

# --- 4. AI Chatbot ---
st.markdown("---")
st.markdown("### 💬 Ask the AI Election Assistant")
st.write("Have any doubts about the process, forms, what to carry, or what to do on polling day? Ask below!")

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chatbot inputs
user_query = st.text_input("Type your question here...", help="Enter any question you have regarding elections, e.g., 'What if I lost my Voter ID?'")
chat_submit = st.button("Ask Assistant", help="Click to send your question to the Gemini AI.")

if chat_submit and user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.spinner("AI is thinking..."):
        answer = get_gemini_response(user_query, context)
        st.session_state.messages.append({"role": "assistant", "content": answer})

# Display mock chat log (latest interactions first for better UX in a static bottom section)
if st.session_state.messages:
    st.write("#### Conversation History")
    for msg in reversed(st.session_state.messages[-6:]):  # show last 6 messages
        if msg["role"] == "user":
            st.markdown(f"**You:** *{msg['content']}*")
        else:
            st.info(f"**Assistant:** {msg['content']}")
