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
3. What does it mean to fine-tune a RAG?
- Fine-tuning the embedding model, retrievers, re-ranker, query-rewriting model , or genetor depending on the where the problem exists. 

4. How do you create a dataset for retrieval fine-tuning? 
5. What are hard negatives?
6. How do you evaluate retrieval? 

7.How do you Evaluate the final RAG answer? 

- Answer Correctness : Is the answer factually right? 
- Groundness : is it based only on retrieved document, not hallacunations?
- Context relevance : does the answer actually match the user's question? 
- Completness : Does it cover all parts of the question, not just partial reply? 
- latancy : how fast was answer generated?
- cost : how much compue or money did it take to produce the answer? 

8. What if retrival is good but the answer is wrong? 

- Prompt constructoin.
- Context ordring.
- context length.
- Generator behaviour.
- Model limitations.

9. What if retrieval is bad? 

Investigate? 
- Chunking.
- Embedding model.
- Qury formulation.
- Metadata Filters
- Serach Strategy
- Reranker
- Docuement Quality.

10. When would you fine-tune embeddings? 

- when generic embedding fails to capture the domain-specefic terminology, relationship, or relavance patterns, and sufficient labeled training data is available. 

Agents 

11 : What is an AI Agent? 

- An AI agent is a system that uses an llm and tools to decide and execute a sequence of actions towrd a goal.

12. Agent VS chatbot?

- A chatbot primarily genrates conversational responses. An Agent can perform actoins thought tools and maintain task state.

13. What is tool calling? 

- tool calling allows the model to request a structured function/API invocation.

14. What are agent failure models?
15. how do you control agent cost?
16. When should NOT use agents?

RAG: 

17. Why is chinking important?
18. What is hybrid search?
19. Why use re-ranker?
20. How many chinks should be retrieved
21. What is RAG hallucination?
22. How can hallucinations be reduced? 
23. What is a vector databse?

System Design:

24: Scenerio:
Design a company-wide knowledge assitant

<<Architecture>>

25. Project cost management. 

26. Cost estimation framework
27. Production Optimization
