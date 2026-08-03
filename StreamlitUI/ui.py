import streamlit as st

# st.title 
st.title("Simple GenAI lookup")

# Input widget
user_prompt = st.text_input("Enter you Prompt")
temprature = st.slider("Creativity , 0.0, 1,0, 0.2")
model_choice = st.selectbox("Choose Model" , ["GPT-5.6 Sol-Quick" ,"GPT-5.6 Terra- Think" , "GPT-5.6 Lun-Logic"])
uploded_file = st.file_uploader("Upload a text file")

# Text area
bio = st.text_area("enter a short bio")
st.write(bio)

hobbies = st.multiselect("Select Hobbies" , ["Reading" , "Coding" ,"Music", "Sports"])
st.write(hobbies)

date = st.date_input("Pick a date")
st.write(date)

time = st.time_input("Pick a time")
st.write(time)

uploded_file = st.file_uploader("upload a file")
if uploded_file:
    st.write("File uploaded: ",uploded_file.name)