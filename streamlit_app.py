import streamlit as st
import google.generativeai as genai
import requests

# 1. Page Config & Professional UI Styling
st.set_page_config(page_title="ArtHeal", page_icon="🎨", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .art-card {
        background-color: white;
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-top: 25px;
        border: 1px solid #f0f0f0;
    }
    .label { 
        color: #999; 
        font-size: 0.75rem; 
        font-weight: 700; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        margin-top: 15px; 
        margin-bottom: 5px;
    }
    .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Secret Key Logic (One Key for All)
try:
    # This looks for the key you just pasted in the Streamlit Secrets vault
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("Missing API Key. Please add 'GEMINI_API_KEY' to Streamlit Secrets.")
    st.stop()

# 3. Main App Header
st.title("🎨 ArtHeal")
st.write("Share your thoughts. Find a reflection in history.")

# 4. Input Area
user_input = st.text_area("", placeholder="How is your heart today?", height=150, label_visibility="collapsed")

# 5. Action Button
if st.button("Consult the Archives", use_container_width=True):
    if user_input:
        try:
            # Using the stable 2.5 Flash model
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""
            User Statement: {user_input}
            Role: Empathetic Art Historian. 
            Task: Identify the emotion, suggest one specific European painting, 
            explain the artist's struggle in 2-3 sentences, and suggest one creative task.
            Return format: Emotion | Artist | Painting | Story | Activity
            """
            
            with st.spinner("Searching the archives..."):
                response = model.generate_content(prompt)
                # Parse the response safely
                parts = [p.strip() for p in response.text.split('|')]
                
                if len(parts) >= 5:
                    emotion, artist, painting, story, activity = parts[0:5]

                    # THE REVEAL
                    st.markdown(f"### I sense a feeling of **{emotion.lower()}**.")
                    
                    with st.container():
                        st.markdown('<div class="art-card">', unsafe_allow_html=True)
                        st.subheader(painting)
                        st.caption(f"By {artist}")
                        
                        # Image Fetching (The Met Museum API)
                        try:
                            search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={painting}"
                            search_res = requests.get(search_url).json()
                            if search_res.get('total', 0) > 0:
                                obj_id = search_res['objectIDs'][0]
                                obj_data = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}").json()
                                st.image(obj_data.get('primaryImageSmall'), use_container_width=True)
                        except:
                            st.info("Story found, but the image is resting in the vault.")

                        st.markdown(f'<p class="label">The Artist\'s Struggle</p><p>{story}</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="label">Reflective Activity</p><p>{activity}</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Secondary Action
                    if st.button("New Reflection"):
                        st.rerun()

        except Exception as e:
            st.error("The archives are quiet. Try a different thought!")
    else:
        st.warning("Please share a thought first.")
