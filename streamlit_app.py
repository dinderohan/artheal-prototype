import streamlit as st
import google.generativeai as genai
import requests

# 1. UI Setup
st.set_page_config(page_title="ArtHeal MVP", page_icon="🎨", layout="centered")
st.title("🎨 ArtHeal: Reflection through History")
st.markdown("### How are you feeling today?")

# 2. Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Paste Gemini API Key", type="password")
    st.info("Get your key from Google AI Studio")

# 3. Main User Input
user_input = st.text_area("Talk to me about what's on your mind...", 
                          placeholder="e.g., I'm feeling like a lone wolf designer on my team...", 
                          height=150)

if st.button("Find My Reflection"):
    if not api_key:
        st.error("Please paste your API key in the sidebar first!")
    elif not user_input:
        st.warning("Please tell me a bit about your feelings first.")
    else:
        try:
            genai.configure(api_key=api_key)
            # Using 2.5 Flash - the current most stable/cost-effective model
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""
            User Statement: {user_input}
            You are an empathetic Art Historian. 
            1. Identify the core emotion.
            2. Map it to a specific European artist/movement that faced a similar struggle.
            3. Provide a practical activity to release that emotion.
            
            Format your response EXACTLY like this:
            Emotion: [Name]
            Artist: [Artist Name]
            Painting: [Exact Painting Title]
            The Story: [2-3 sentences on the artist's struggle and how this work helped them]
            Activity: [One simple, practical creative task]
            """
            
            with st.spinner("Consulting the archives..."):
                response = model.generate_content(prompt)
                res_text = response.text
                
                # Split the text into parts to show it nicely
                st.divider()
                st.markdown(res_text)

                # 4. Search for the Artwork Image (The Met Museum)
                try:
                    # Clean up the painting name for searching
                    painting_title = res_text.split("Painting:")[1].split("\n")[0].strip()
                    search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={painting_title}"
                    search_req = requests.get(search_url).json()
                    
                    if search_req.get('total', 0) > 0:
                        obj_id = search_req['objectIDs'][0]
                        obj_data = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}").json()
                        img_url = obj_data.get('primaryImageSmall')
                        
                        if img_url:
                            st.image(img_url, caption=f"{painting_title}")
                        else:
                            st.info("I found the history, but couldn't find a public-domain image for this specific piece.")
                except Exception as img_err:
                    st.write("*(Note: Found the story, but had trouble loading the visual. Focus on the activity above!)*")

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
            st.info("Check your API key or try again in a moment.")
