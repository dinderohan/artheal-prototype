import streamlit as st
import google.generativeai as genai
import requests

# 1. UI Configuration & Professional Styling
st.set_page_config(page_title="ArtHeal", page_icon="🎨", layout="centered")

# WCAG AA Compliant Blue: #1A56BE
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
    
    /* Ensure image doesn't overflow on mobile */
    img { border-radius: 12px; max-width: 100%; height: auto; }
    </style>
    """, unsafe_allow_html=True)

# 2. Key Check (using Streamlit Secrets)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("API Key missing in Secrets! Check your Streamlit Cloud settings.")
    st.stop()

# 3. Sticky Header
st.markdown('<div class="sticky-nav"><span style="font-weight:700; font-size:1.2rem;">🎨 ArtHeal</span></div>', unsafe_allow_html=True)
st.markdown('<div class="main-content"></div>', unsafe_allow_html=True)

# 4. Input Flow
user_input = st.text_area("", placeholder="How is your heart today?", height=120, label_visibility="collapsed")

col_a, col_b = st.columns([0.7, 0.3])
with col_a:
    submit = st.button("Consult the Archives", use_container_width=True, type="primary")
with col_b:
    if st.button("New Chat", use_container_width=True):
        st.rerun()

# 5. Helper Function: Global Art Search (Wikipedia + The Met)
def fetch_art_image(painting, artist):
    # Try Wikipedia first (Great for global/European works like Munch, Van Gogh)
    try:
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={painting}&prop=pageimages&format=json&pithumbsize=800"
        res = requests.get(wiki_url).json()
        pages = res.get("query", {}).get("pages", {})
        for pg in pages:
            if "thumbnail" in pages[pg]:
                return pages[pg]["thumbnail"]["source"]
    except: pass
    
    # Fallback to The Met API
    try:
        search_term = f"{painting} {artist}"
        met_search = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={search_term}").json()
        if met_search.get('total', 0) > 0:
            obj_id = met_search['objectIDs'][0]
            obj_data = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}").json()
            return obj_data.get('primaryImageSmall')
    except: return None

# 6. Execution Logic
if submit and user_input:
    try:
        # Use 1.5 Flash for speed and strict formatting
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        User input: {user_input}
        Role: Expert Art Historian. Map the emotion to a REAL famous European painting.
        
        Strict Requirements:
        - Identify the real historical context (Spark/Before), the actual technique used (Creation/During), and the aftermath (Impact/After). 
        - Do NOT hallucinate. Use only verified historical facts.
        - The activity must be a simple, actionable 1-sentence physical task.
        
        Return exactly this format:
        Emotion | Artist | Painting | The Spark | The Creation | The Impact | Activity
        """
        
        with st.spinner("Consulting history..."):
            response = model.generate_content(prompt)
            data = [part.strip() for part in response.text.split('|')]
            
            if len(data) >= 7:
                emotion, artist, painting, spark, creation, impact, activity = data[0:7]
                
                # Visual Reveal
                st.markdown(f"#### I hear your **{emotion.lower()}**.")
                
                # The Content Block (No empty container, renders on demand)
                st.subheader(painting)
                st.caption(f"By {artist}")
                
                # Image Display
                img_url = fetch_art_image(painting, artist)
                if img_url:
                    st.image(img_url, use_container_width=True)
                else:
                    st.info("Found the history, but the visual remains in the Oslo archives. Visualize the brushstrokes in your mind.")

                # The Factual Process
                st.markdown('<p class="blue-label">The Process</p>', unsafe_allow_html=True)
                st.markdown(f"**The Spark:** {spark}")
                st.markdown(f"**The Creation:** {creation}")
                st.markdown(f"**The Impact:** {impact}")
                
                # The Task
                st.markdown('<p class="blue-label">Reflective Activity</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="activity-box"><b>Try this:</b> {activity}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error("The archives are currently quiet. Try expressing a different thought.")
