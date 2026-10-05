import os
import pathlib
import streamlit as st
import chromadb
import requests
from dotenv import load_dotenv

# Automatically find and load the .env file from the main STA-Tutor folder
env_path = pathlib.Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Custom API configuration
CUSTOM_API_URL = os.getenv("CUSTOM_API_URL", "https://api.fadher.tech/v1/rag-chat")
CUSTOM_API_KEY = os.getenv("CUSTOM_API_KEY")

if not CUSTOM_API_KEY:
    st.error("CUSTOM_API_KEY not found! Please check your .env file.")
    st.stop()

# Paths
DB_DIR = os.path.join("data", "vector_db")

@st.cache_resource
def get_chroma_collection():
    db_client = chromadb.PersistentClient(path=DB_DIR)
    return db_client.get_or_create_collection(name="sta_materials")

collection = get_chroma_collection()

# Streamlit UI Design
st.set_page_config(page_title="STA Tutor", page_icon="🤖", layout="centered")
st.title("🎓 STA Tutor")
st.write("Your personal AI assistant for Software Testing and Assurance. Ask me anything about your course notes!")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input box
if prompt := st.chat_input("What would you like to know about Software Testing?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching course notes and thinking..."):
            try:
                # 1. Search ChromaDB for relevant text chunks
                results = collection.query(
                    query_texts=[prompt],
                    n_results=3 # Get top 3 most relevant paragraphs
                )
                retrieved_chunks = results["documents"][0] if results["documents"] else []
                sources = results["metadatas"][0] if results["metadatas"] else []

                # 2. Build context string from retrieved chunks
                context = "\n\n".join(retrieved_chunks)

                # 3. Construct prompt for Custom LLM
                system_instruction = (
                    "You are STA Tutor, a helpful university teaching assistant for a Software Testing and Assurance course. "
                    "Answer the student's question accurately using *only* the provided course context below. "
                    "If the answer cannot be found in the context, politely say you couldn't find it in the course notes."
                )

                full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

                # 4. Call Custom API
                headers = {
                    "Authorization": f"Bearer {CUSTOM_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {"query": full_prompt}
                
                response = requests.post(CUSTOM_API_URL, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                answer = result.get("answer", result.get("response", str(result)))

                st.markdown(answer)

                # Optional: Show sources neatly
                if sources:
                    with st.expander("📚 View Course Sources"):
                        for src in sources:
                            st.write(f"- File: `{src['source']}`, Page: {src['page']}")

                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                error_msg = f"An error occurred: {e}"
                st.error(error_msg)