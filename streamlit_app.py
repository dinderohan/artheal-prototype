import streamlit as st
import google.generativeai as genai
import requests

# 1. UI Configuration
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
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # STRICT PROMPT: No more placeholders.
        prompt = f"""
        User input: {user_input}
        Role: Expert Art Historian & Empath.
        
        Instruction: 
        1. Find a REAL famous European painting that mirrors this emotion.
        2. Describe the actual historical 'Spark' (intent), the 'Creation' (technique used), and 'Impact' (aftermath).
        3. Do NOT use the words 'Before', 'During', or 'After' as the content. Provide rich, crisp descriptions.
        
        Return exactly this format:
        Emotion: [1 word]
        Artist: [Name]
        Painting: [Full Title]
        Spark: [Real historical context of why it was made]
        Creation: [Specific artistic detail or process used]
        Impact: [How it affected the artist or society]
        Activity: [One simple, verb-led task for the user]
        
        Format parts separated by the '|' character.
        """
        
        with st.spinner("Consulting the archives..."):
            response = model.generate_content(prompt)
            # Split by pipe and strip whitespace/newlines
            p = [part.strip() for part in response.text.replace('\n', '').split('|')]
            
            # Cleaning labels from the AI response if it included them
            clean_p = [part.split(':')[-1].strip() for part in p]

            if len(clean_p) >= 7:
                st.markdown(f"#### I hear your **{clean_p[0].lower()}**.")
                
                st.subheader(clean_p[2])
                st.caption(f"By {clean_p[1]}")
                
                # Image Search
                search_term = f"{clean_p[2]} {clean_p[1]}"
                search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={search_term}"
                search_res = requests.get(search_url).json()
                if search_res.get('total', 0) > 0:
                    obj_id = search_res['objectIDs'][0]
                    obj_data = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}").json()
                    if obj_data.get('primaryImageSmall'):
                        st.image(obj_data['primaryImageSmall'], use_container_width=True)

                # Process Breakdown
                st.markdown(f'<p class="blue-label">The Process</p>', unsafe_allow_html=True)
                st.markdown(f"**The Spark:** {clean_p[3]}")
                st.markdown(f"**The Creation:** {clean_p[4]}")
                st.markdown(f"**The Impact:** {clean_p[5]}")
                
                # Activity
                st.markdown(f'<p class="blue-label">Your Reflection</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="activity-box"><b>Try this:</b> {clean_p[6]}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error("The archives are quiet. Try a different thought!")
