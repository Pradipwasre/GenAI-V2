first call? Majority : 

What are tokens? 
- llm text ko word nahi, read in the tokens = 9 tokens

-- High Tokens : high money
-- high tokens : High Latency
-- High tokens : High context

What are embeddings? 

- text ko number ke list (vector) main convert karna , because of that the computer should understand the sentence meaning.

Example:
    - how do i reset my password?
    - i fotgot my password. What's the recovery process?

Google , youtube : Car ---> Automobiles

how the Similarity get happend ? 
- Cosine similarity (angle between two vector) Angle is low, then high similarity



Q3 : What is RAG: 

- user first takes the query
- query process the data
- Retriever picked chunks from vector store
- prompt = Query + context (answer)
- llm answer

Q4 : what is document chunking.

- larger text : cutting in the specefied numbers 
- 10,000 : 1000 : 10 chunks.

-------------------
1. What is RAG? 
2. Why no simply fine-tune the model on company documents?
 