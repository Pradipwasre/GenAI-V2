import streamlit as st


st.title("Hello World")
st.subheader("Enterprise Data Hub")
st.markdown("##### *Turn raw operational data into actionable business intelligence.*")
st.write("Key Performance Indicators (KPIs)")


if st.button("Run"):
    st.write("Verifying server")

st.title("Buttons")

if st.button("Extract"):
    st.write("Extracting the Data")


if st.button("Transform"):
    st.write("Transforming the Data")

if st.button("Load"):
    st.write("Loading the data")


name = st.text_input("Enter your model name")
st.write(name)

age = st.number_input("Enter you Age")
st.write(age)


temprature = st.slider("Set the Model temprature" , 0 , 45)
st.write(temprature)


city = st.selectbox(
    "Choose the Model",
    ["llama" , "GPT-4o" , "Gemini" , "Kimi"]
)

st.write(city)

agree = st.checkbox("I Agree")
st.write(agree)

gender = st.radio(
    "Select Gender",
    ["Male", "Female"]
)

st.write(gender)


st.success("Data Load Successful!")

st.error("Wrong API Key Loaded")