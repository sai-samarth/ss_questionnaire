import streamlit as st
import pandas as pd
import os
import time
import json
from supabase import create_client

# Initialize Supabase
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)

# Title of the form
# st.title("Audio Feedback Form")

# Pre-defined audio files (replace with your own file paths or URLs)

json_file = "audio_new.json"
with open(json_file, "r") as f:
    audio_files = json.load(f)
# CSV file path
csv_file = "feedback.csv"

# Initialize session state to track the current audio file index and user nickname
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "nickname" not in st.session_state:
    st.session_state.nickname = ""

# Ask for nickname only once
if st.session_state.current_index == 0 and not st.session_state.nickname:
    st.session_state.nickname = st.text_input("Provide your nickname and press 'Enter':", "")
    if not st.session_state.nickname:
        st.stop()

# Function to display loading screen
def show_loading():
    st.markdown("""
        <style>
        .loading-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: black;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 18px;
            color: white;
            font-weight: bold;
            z-index: 9999;
        }
        </style>
        <div class="loading-container">Loading next audio...</div>
    """, unsafe_allow_html=True)
    time.sleep(.5)

# Get the current audio file
current_audio = audio_files[st.session_state.current_index]

# Display the current audio file name
st.write(f"### **{current_audio['name']} of 40**")

# Display the audio player
st.audio(current_audio["path"], format='audio/wav')

# Display the correct transcription
st.write("#### Correct Transcription:")

# Display the correct transcription in blue color
st.markdown(f"<h4 style='color:yellow;'>{current_audio['transcription']}</h4>", unsafe_allow_html=True)

# Reduce font sizes to fit everything on one page
st.markdown("#### Please rate the audio based on the following criteria:")

def horizontal_radio(label, options, index=2):
    st.markdown(f"<h4 style='font-size:20px;'>{label}</h4>", unsafe_allow_html=True)
    return st.select_slider(" ", options=options, value=options[index], format_func=lambda x: x, key=label)

intelligibility = horizontal_radio(
    "1. Intelligibility: Can you clearly understand every word?",
    ["1 - Strongly Disagree", "2 - Disagree", "3 - Neutral", "4 - Agree", "5 - Strongly Agree"],
    index=2
)

naturalness = horizontal_radio(
    "2. Naturalness: Did the voice sound natural and human-like?",
    ["1 - Strongly Disagree", "2 - Disagree", "3 - Neutral", "4 - Agree", "5 - Strongly Agree"],
    index=2
)

pronunciation = horizontal_radio(
    "3. Pronunciation Accuracy: Were all words pronounced clearly and correctly?",
    ["1 - Strongly Disagree", "2 - Disagree", "3 - Neutral", "4 - Agree", "5 - Strongly Agree"],
    index=2
)

# Function to save feedback to supabase
def save_feedback(nickname, audio_name, intelligibility, naturalness, pronunciation):
    feedback_data = {
        "nickname": nickname,
        "audio_name": audio_name,
        "intelligibility": intelligibility.split(" - ")[0],
        "naturalness": naturalness.split(" - ")[0],
        "pronunciation": pronunciation.split(" - ")[0]
    }
    
    result = supabase.table('feedback').insert(feedback_data).execute()
    return result

# Next button to proceed to the next audio file
if st.button("Next"):
    # Save the current rating
    save_feedback(st.session_state.nickname, current_audio['name'], intelligibility, naturalness, pronunciation)    
    # Move to the next audio file
    st.session_state.current_index += 1

    # Check if all audio files have been evaluated
    if st.session_state.current_index >= len(audio_files):
        st.success("Thank you for completing the survey!")
        st.session_state.current_index = 0  # Reset to the first audio file
    else:
        show_loading()
        st.rerun()  # Refresh the page to show the next audio file
