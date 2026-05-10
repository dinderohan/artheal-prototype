import streamlit as st
import google.generativeai as genai
import requests

# 1. Advanced CSS: Sticky Header, Cards, and Dark Mode Support
st.set_page_config(page_title="ArtHeal", page_icon="🎨", layout="centered")

# WCAG AA Compliant Blue: #1A56BE
st.markdown("""
    <style>
    /* Sticky Header Logic */
    div[data-testid="stVerticalBlock"] > div:has(div.sticky-header) {
        position: sticky;
        top: 2.8rem;
        background-color: transparent;
        z-index: 999;
    }
    .sticky-header {
        background-color: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 10px 20px;
        border-radius: 0 0 15px 15px;
        border-bottom: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    /* Dark Mode Overrides */
    @media (prefers-color-scheme: dark) {
        .sticky-header {
            background-color: rgba(14, 17, 23, 0.9);
            border-bottom: 1px solid #333;
        }
        .art-card { background-color: #1E2329 !important; border: 1px solid #333 !important; }
    }

    .art-card {
        background-color: white;
        padding: 24px;
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    
    /* WCAG Blue Headers */
    .blue-label { 
        color: #1A56BE; 
        font-size: 0.75rem; 
        font-weight: 800; 
        text-transform: uppercase; 
        letter-spacing: 1.2px;
        margin-top: 20px; 
    }
    
    .activity-box {
        background-color: #f0f5ff;
        padding: 18px;
        border-radius: 12px;
        margin-top: 10px;
        color: #1A56BE;
        border: 1px solid #dbe9ff;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Key Check
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("API Key missing in Secrets!")
    st.stop()

# 3. The Sticky Header Component
with st.container():
    st.markdown('<div class="sticky-header">', unsafe_allow_html=True)
    col_t, col_b = st.columns([0.8, 0.2])
    with col_t:
        st.markdown("### 🎨 ArtHeal")
    with col_b:
        if st.button("New", help="Start a new reflection"):
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 4. Input Flow
user_input = st.text_area("", placeholder="What's on your mind?", height=120, label_visibility="collapsed")

if st.button("Consult the Archives", use_container_width=True, type="primary"):
    if user_input:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = f"User: {user_input}. Output Emotion, Artist, Painting, StoryTitle, StoryBody, ActivityTitle, ActivityBody. Format: Emotion|Artist|Painting|StoryTitle|StoryBody|ActivityTitle|ActivityBody"
            
            with st.spinner("Finding your reflection..."):
                response = model.generate_content(prompt)
                parts = [p.strip() for p in response.text.split('|')]
                
                if len(parts) >= 7:
                    # Clearer UI presentation
                    st.markdown(f"#### I hear your **{parts[0].lower()}**.")
                    
                    # ONLY render the card if we have content (prevents the ghost box)
                    with st.container():
                        st.markdown('<div class="art-card">', unsafe_allow_html=True)
                        st.subheader(parts[2])
                        st.caption(f"By {parts[1]}")
                        
                        # Smart Image Search
                        search_term = f"{parts[2]} {parts[1]}"
                        search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={search_term}"
                        search_res = requests.get(search_url).json()
                        if search_res.get('total', 0) > 0:
                            obj_id = search_res['objectIDs'][0]
                            obj_data = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}").json()
                            if obj_data.get('primaryImageSmall'):
                                st.image(obj_data['primaryImageSmall'], use_container_width=True)
                        
                        st.markdown(f'<p class="blue-label">{parts[3]}</p>', unsafe_allow_html=True)
                        st.write(parts[4])
                        
                        st.markdown(f'<p class="blue-label">Your Activity</p>', unsafe_allow_html=True)
                        st.markdown(f'<div class="activity-box"><b>{parts[5]}</b><br>{parts[6]}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error("The archives are quiet. Try a different thought!")
