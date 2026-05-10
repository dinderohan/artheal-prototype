import streamlit as st
import google.generativeai as genai
import requests

# 1. UI Configuration & Responsive CSS
st.set_page_config(page_title="ArtHeal", page_icon="🎨", layout="centered")

# WCAG AA Compliant Blue: #1A56BE
st.markdown("""
    <style>
    /* Sticky Header Styling */
    .sticky-nav {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: var(--background-color);
        padding: 10px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        z-index: 999999;
    }
    
    /* Card Styling using Theme Variables for perfect Dark/Light support */
    .art-card {
        background-color: var(--secondary-background-color);
        padding: 24px;
        border-radius: 20px;
        margin-top: 20px;
        border: 1px solid rgba(128, 128, 128, 0.1);
    }
    
    .blue-label { 
        color: #1A56BE; 
        font-size: 0.75rem; 
        font-weight: 800; 
        text-transform: uppercase; 
        letter-spacing: 1.2px;
        margin-top: 20px; 
        margin-bottom: 5px;
    }
    
    .activity-box {
        background-color: rgba(26, 86, 190, 0.05);
        padding: 15px;
        border-left: 4px solid #1A56BE;
        border-radius: 8px;
        margin-top: 10px;
    }
    
    /* Ensuring the main content doesn't get hidden under the sticky header */
    .main-content { margin-top: 60px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Key Check
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Missing API Key in Secrets!")
    st.stop()

# 3. The Sticky Header (Anchor)
st.markdown(f'''
    <div class="sticky-nav">
        <span style="font-weight:700; font-size:1.2rem;">🎨 ArtHeal</span>
    </div>
''', unsafe_allow_html=True)

# Add spacing for the header
st.markdown('<div class="main-content"></div>', unsafe_allow_html=True)

# 4. Input Flow
user_input = st.text_area("", placeholder="How is your heart today?", height=120, label_visibility="collapsed")

col_a, col_b = st.columns([0.7, 0.3])
with col_a:
    submit = st.button("Consult the Archives", use_container_width=True, type="primary")
with col_b:
    if st.button("New Chat", use_container_width=True):
        st.rerun()

# 5. Logic Execution
if submit and user_input:
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"User: {user_input}. Output Emotion, Artist, Painting, StoryTitle, StoryBody, ActivityTitle, ActivityBody. Format: Emotion|Artist|Painting|StoryTitle|StoryBody|ActivityTitle|ActivityBody"
        
        with st.spinner("Finding your reflection..."):
            response = model.generate_content(prompt)
            parts = [p.strip() for p in response.text.split('|')]
            
            if len(parts) >= 7:
                st.markdown(f"#### I hear your **{parts[0].lower()}**.")
                
                # The Card Container (Now only renders when results exist)
                st.markdown('<div class="art-card">', unsafe_allow_html=True)
                st.subheader(parts[2])
                st.caption(f"By {parts[1]}")
                
                # Image Search Logic
                search_term = f"{parts[2]} {parts[1]}"
                search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={search_term}"
                search_res = requests.get(search_url).json()
                if search_res.get('total', 0) > 0:
                    obj_id = search_res['objectIDs'][0]
                    obj_data = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}").json()
                    if obj_data.get('primaryImageSmall'):
                        st.image(obj_data['primaryImageSmall'], use_container_width=True)
                
                # Story
                st.markdown(f'<p class="blue-label">{parts[3]}</p>', unsafe_allow_html=True)
                st.write(parts[4])
                
                # Activity
                st.markdown(f'<p class="blue-label">Reflective Activity</p>', unsafe_allow_html=True)
                st.markdown(f'''
                    <div class="activity-box">
                        <strong style="color:#1A56BE;">{parts[5]}</strong><br>
                        <span style="color: inherit;">{parts[6]}</span>
                    </div>
                ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error("The archives are quiet. Try a different thought!")
