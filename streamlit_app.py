import streamlit as st
import google.generativeai as genai
import requests

# 1. Setup Page & Title
st.set_page_config(page_title="ArtHeal MVP", page_icon="🎨")
st.title("🎨 ArtHeal: Reflection through History")
st.markdown("### How are you feeling today?")

# 2. Connect your Gemini (Enter your key in the sidebar)
with st.sidebar:
    api_key = st.text_input("Paste Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)

# 3. The Input
user_input = st.text_area("Talk to me about what's on your mind...", height=150)

if st.button("Find My Reflection") and user_input:
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompting Gemini to act as your art historian
    prompt = f"""
    User is feeling: {user_input}
    1. Identify the core emotion.
    2. Suggest a famous European painting that reflects a similar struggle/solution.
    3. Return exactly in this format: 
    Emotion: [Emotion]
    Artist: [Artist Name]
    Painting: [Exact Painting Name]
    Story: [2 sentences on how the artist used this to heal]
    Activity: [One simple creative activity]
    """
    
    with st.spinner("Searching art history..."):
        response = model.generate_content(prompt)
        res_text = response.text
        st.write(res_text)

        # 4. Attempt to find the image via The Met API (Simple search)
        # For a dirty prototype, we just grab the first matching result
        painting_name = res_text.split("Painting:")[1].split("\n")[0].strip()
        met_search = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={painting_name}"
        search_res = requests.get(met_search).json()
        
        if search_res.get('objectIDs'):
            obj_id = search_res['objectIDs'][0]
            obj_data = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}").json()
            st.image(obj_data['primaryImageSmall'], caption=painting_name)
