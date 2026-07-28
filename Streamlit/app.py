import streamlit as st

st.title("Blinkit Price Predictor")

name = st.text_input("Product Name")

weight = st.number_input("Weight")

rating = st.slider("Rating" , 1, 5)

category = st.selectbox(
    "Category",
    ["Snacks" , "Milk" , "Fruits"]
)

if st.button("Predict Price"):
    st.success("Prediction Completed")