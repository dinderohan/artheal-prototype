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
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
        margin-top: 20px;
        border: 1px solid #f2f2f2;
    }
    .label { 
        color: #A0A0A0; 
        font-size: 0.7rem; 
        font-weight: 800; 
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        margin-top: 20px; 
        margin-bottom: 8px;
    }
    .activity-box {
        background-color: #f8faff;
        padding: 15px;
        border-left: 4px solid #4A90E2;
        border-radius: 8px;
        margin-top: 10px;
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

st.title("🎨 ArtHeal")
st.write("Share your heart. Find your reflection.")

user_input = st.text_area("", placeholder="What's on your mind?", height=120, label_visibility="collapsed")

if st.button("Consult the Archives", use_container_width=True):
    if user_input:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # IMPROVED PROMPT: Clearer instructions for 'Story' and 'Activity'
            prompt = f"""
            User: {user_input}
            Role: Art Historian & Empath.
            Output: Identify the emotion, one European painting, the artist's struggle story, and a clear step-by-step activity.
            
            Return format exactly like this:
            EMOTION: [1 word]
            ARTIST: [Name]
            PAINTING: [Exact Title]
            STORY_TITLE: [A 3-4 word title for the artist's struggle]
            STORY_BODY: [2 sentences on how the artist used this work to overcome the emotion]
            ACTIVITY_TITLE: [A short title for the action]
            ACTIVITY_BODY: [One specific, practical instruction starting with a verb]
            """
            
            with st.spinner("Searching art history..."):
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                data = {l.split(':')[0].strip(): l.split(':')[1].strip() for l in lines if ':' in l}

                # 3. The Visual Reveal
                st.markdown(f"### I sense a feeling of **{data['EMOTION'].lower()}**.")
                
                with st.container():
                    st.markdown('<div class="art-card">', unsafe_allow_html=True)
                    st.subheader(data['PAINTING'])
                    st.caption(f"By {data['ARTIST']}")
                    
                    # SMART SEARCH: Search by "Painting Name + Artist" for better results
                    search_term = f"{data['PAINTING']} {data['ARTIST']}"
                    search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={search_term}"
                    search_res = requests.get(search_url).json()
                    
                    if search_res.get('total', 0) > 0:
                        obj_id = search_res['objectIDs'][0]
                        obj_data = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}").json()
                        if obj_data.get('primaryImageSmall'):
                            st.image(obj_data['primaryImageSmall'], use_container_width=True)
                    
                    # Story Section
                    st.markdown(f'<p class="label">{data["STORY_TITLE"]}</p>', unsafe_allow_html=True)
                    st.write(data['STORY_BODY'])
                    
                    # Activity Section
                    st.markdown(f'<p class="label">Your Personal Activity</p>', unsafe_allow_html=True)
                    st.markdown(f"""
                        <div class="activity-box">
                            <strong>{data['ACTIVITY_TITLE']}</strong><br>
                            {data['ACTIVITY_BODY']}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error("The archives are quiet. Try a different thought!")
