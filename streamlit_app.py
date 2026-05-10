import streamlit as st
import google.generativeai as genai
import requests

# 1. UI Configuration (Clean & Minimal)
st.set_page_config(page_title="ArtHeal", page_icon="🎨", layout="centered")

st.markdown("""
    <style>
    .sticky-nav {
        position: fixed; top: 0; left: 0; width: 100%;
        background: var(--background-color); padding: 10px 20px;
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2); z-index: 9999;
    }
    .blue-label { 
        color: #1A56BE; font-size: 0.75rem; font-weight: 800; 
        text-transform: uppercase; letter-spacing: 1.2px;
        margin-top: 25px; margin-bottom: 5px;
    }
    .activity-box {
        background-color: rgba(26, 86, 190, 0.05);
        padding: 15px; border-left: 4px solid #1A56BE;
        border-radius: 8px; margin-top: 10px;
    }
    .main-content { margin-top: 70px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Key Check
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Missing API Key in Secrets!")
    st.stop()

# 3. Header
st.markdown('<div class="sticky-nav"><span style="font-weight:700; font-size:1.2rem;">🎨 ArtHeal</span></div>', unsafe_allow_html=True)
st.markdown('<div class="main-content"></div>', unsafe_allow_html=True)

# 4. Input Area
user_input = st.text_area("", placeholder="How is your heart today?", height=120, label_visibility="collapsed")

col_a, col_b = st.columns([0.7, 0.3])
with col_a:
    submit = st.button("Consult the Archives", use_container_width=True, type="primary")
with col_b:
    if st.button("New Chat", use_container_width=True):
        st.rerun()

# 5. The Logic
if submit and user_input:
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # GROUNDED PROMPT: Focus on Art History Facts & Process
        prompt = f"""
        User input: {user_input}
        Role: Fact-based Art Historian.
        Task: Map the user's emotion to a REAL European painting and its historical context.
        
        Provide the following exactly:
        - Emotion: [1 word]
        - Artist: [Name]
        - Painting: [Title]
        - Before: [The real-life struggle or event that led the artist to start this]
        - During: [A specific technique or detail about the making process]
        - After: [The result for the artist or society]
        - Activity: [A 1-sentence actionable task]

        Format: Emotion|Artist|Painting|Before|During|After|Activity
        """
        
        with st.spinner("Consulting history..."):
            response = model.generate_content(prompt)
            p = [part.strip() for part in response.text.split('|')]
            
            if len(p) >= 7:
                st.markdown(f"#### I hear your **{p[0].lower()}**.")
                
                # Content Display (No Container Box)
                st.subheader(p[2])
                st.caption(f"By {p[1]}")
                
                # Image Search
                search_term = f"{p[2]} {p[1]}"
                search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={search_term}"
                search_res = requests.get(search_url).json()
                if search_res.get('total', 0) > 0:
                    obj_id = search_res['objectIDs'][0]
                    obj_data = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}").json()
                    if obj_data.get('primaryImageSmall'):
                        st.image(obj_data['primaryImageSmall'], use_container_width=True)

                # Crisp Process Breakdown
                st.markdown(f'<p class="blue-label">The Process</p>', unsafe_allow_html=True)
                st.markdown(f"**The Spark:** {p[3]}")
                st.markdown(f"**The Creation:** {p[4]}")
                st.markdown(f"**The Impact:** {p[5]}")
                
                # Activity
                st.markdown(f'<p class="blue-label">Your Reflection</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="activity-box"><b>Try this:</b> {p[6]}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error("The archives are quiet. Try a different thought!")
