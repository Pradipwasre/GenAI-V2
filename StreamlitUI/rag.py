import streamlit as st
import pandas as pd

st.title("RAG with langchain")

uploaded_file = st.file_uploader("Upload a Document (PDF , TXT , CSV)")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("CSV uploded successfully!")
        st.write("preview of Data: ")
        st.dataframe(df.head(10))
    except Exception as e:
        st.error("Error reading csv file" + str(e))

query = st.text_input("Enter your question")
st.write("Query: " , query)

# Slider (for similarity threshold of number of results)
top_k = st.slider("Number of results to retrive" ,1,10,3)
st.write("Tok-k Value" , top_k)

embedding_model = st.selectbox("Choose Embedding Model:", ["OpenAI Embedding", "Hugging Face", "Lava"])
st.write("Selected Emebeddings Model:" , embedding_model)

retrival_type = st.radio("Select Retrieval Type" , ["Vector Search" , "BM25","Hybrid"])
st.write(retrival_type)

if st.button("Run RAG"):
    st.write("Last query stored in session")



