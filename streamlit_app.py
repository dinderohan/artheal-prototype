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
        color: #1A56BE; 
        font-size: 0.7rem; 
        font-weight: 800; 
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        margin-top: 20px; 
        margin-bottom: 8px;
    }
    .insight-box {
        background-color: #f0f4f8;
        padding: 15px;
        border-radius: 12px;
        margin-top: 10px;
        font-style: italic;
        color: #334e68;
    }
    .activity-box {
        background-color: #f8faff;
        padding: 15px;
        border-left: 4px solid #1A56BE;
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

# Helper: Dual Search Logic (Wikipedia + Met)
def fetch_art_image(painting, artist):
    try:
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={painting}&prop=pageimages&format=json&pithumbsize=800"
        res = requests.get(wiki_url).json()
        pages = res.get("query", {}).get("pages", {})
        for pg in pages:
            if "thumbnail" in pages[pg]:
                return pages[pg]["thumbnail"]["source"]
    except: pass
    try:
        search_term = f"{painting} {artist}"
        met_res = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={search_term}").json()
        if met_res.get('total', 0) > 0:
            obj_id = met_res['objectIDs'][0]
            obj_data = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}").json()
            return obj_data.get('primaryImageSmall')
    except: return None

st.title("🎨 ArtHeal")
st.write("Share your heart. Find your reflection.")

user_input = st.text_area("", placeholder="What's on your mind?", height=120, label_visibility="collapsed")

if st.button("Consult the Archives", use_container_width=True):
    if user_input:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # REFINED PROMPT: Shifting to Therapeutic Insight
            prompt = f"""
            User: {user_input}
            Role: Art Therapist. 
            Instruction: Provide deep emotional validation and link it to a REAL painting.
            
            Return format exactly like this:
            EMOTION: [1 word]
            VALIDATION: [One sentence validating why the user feels this way]
            ARTIST: [Name]
            PAINTING: [Exact Title]
            METAPHOR: [Identify ONE specific visual detail in the art—a color, a line, or a shadow—and explain how it represents the user's specific struggle]
            STORY_BODY: [2 sentences on the artist's real historical struggle]
            ACTIVITY_BODY: [One specific, sensory task starting with a verb]
            QUESTION: [One deep reflective question to leave the user with]
            """
            
            with st.spinner("Consulting the archives..."):
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                data = {l.split(':')[0].strip(): l.split(':')[1].strip() for l in lines if ':' in l}

                # 3. The Therapeutic Flow
                st.markdown(f"### {data['VALIDATION']}")
                
                with st.container():
                    st.markdown('<div class="art-card">', unsafe_allow_html=True)
                    st.subheader(data['PAINTING'])
                    st.caption(f"By {data['ARTIST']}")
                    
                    # Image Logic
                    img_url = fetch_art_image(data['PAINTING'], data['ARTIST'])
                    if img_url:
                        st.image(img_url, use_container_width=True)
                    
                    # Insight Section
                    st.markdown(f'<p class="label">The Visual Metaphor</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="insight-box">{data["METAPHOR"]}</div>', unsafe_allow_html=True)
                    
                    # Story Section
                    st.markdown(f'<p class="label">The Artist\'s Journey</p>', unsafe_allow_html=True)
                    st.write(data['STORY_BODY'])
                    
                    # Activity Section
                    st.markdown(f'<p class="label">A Somatic Action</p>', unsafe_allow_html=True)
                    st.markdown(f"""
                        <div class="activity-box">
                            <strong>Your Task:</strong><br>
                            {data['ACTIVITY_BODY']}
                        </div>
                    """, unsafe_allow_html=True)

                    st.divider()
                    st.markdown(f"**Reflection:** {data['QUESTION']}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error("The archives are quiet. Try a different thought!")
