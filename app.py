import os, dotenv
import streamlit as st
import sqlite3
from PIL import Image
import io
import re
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
dotenv.load_dotenv()

# API keys


os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# Streamlit configuration
st.set_page_config(page_title="UNIS Tech Support Chat", layout="wide", page_icon="📚")

# Title
st.markdown("""
    <h1 style='text-align: center;'>
        <span style='color: #0071ba;'>UNIS Tech Support Chat</span>
    </h1>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## **About Unis Chat**")
    st.write("Ask tech support questions here and receive answers with source material.")
    st.divider()

# Constants
DATABASE_DIR = "db/updated-db"  # Match the path from your embedding script
IMAGE_DB_PATH = "db/images.db"   # Match the path from your embedding script

# Load vectorstore only once
@st.cache_resource
def load_vectorstore():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    try:
        vectorstore = FAISS.load_local(DATABASE_DIR, embeddings, allow_dangerous_deserialization=True)
        print('Vector Database has been initialized')
        return vectorstore
    except Exception as e:
        st.error(f"Failed to load vector database: {e}")
        return None

# Initialize vectorstore
if "vectorstore" not in st.session_state:
    st.session_state["vectorstore"] = load_vectorstore()
    if st.session_state["vectorstore"] is None:
        st.stop()

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = [
        {"role":"assistant", "content":"Hey there! How can I assist you today?"}
    ]

def format_docs(docs):
    return "\n\n".join(
        [f'Document {i+1}:\n{doc.page_content}\n'
         f'Source: {doc.metadata.get("source", "Unknown")}\n'
         f'Page Number: {doc.metadata.get("page", "Unknown")}\n'
         for i, doc in enumerate(docs)]
    )

# Function to check if query is about manuals/technical content
def is_manual_related_query(query):
    # Keywords that suggest the query is about technical manuals
    manual_keywords = [
        'manual', 'instruction', 'guide', 'how to', 'steps', 'procedure',
        'fix', 'repair', 'install', 'setup', 'configure', 'operate',
        'button', 'switch', 'panel', 'screen', 'display', 'menu',
        'error', 'problem', 'issue', 'troubleshoot', 'diagnostics',
        'part', 'component', 'assembly', 'connection', 'wire', 'plug',
        'specification', 'dimension', 'measurement', 'setting', 'adjustment'
    ]
    
    # Convert query to lowercase for matching
    query_lower = query.lower()
    
    # Check for manual-related keywords
    for keyword in manual_keywords:
        if keyword in query_lower:
            return True
    
    # More aggressive check for technical questions
    if re.search(r'(what|how|where|when|why|which).*(\?|$)', query_lower):
        # If it's a question, check similarity to our vectors
        try:
            results = st.session_state["vectorstore"].similarity_search_with_score(query, k=1)
            if results and len(results) > 0:
                # If similarity score is high enough, it's likely manual-related
                _, score = results[0]
                # Threshold determined by your vector space characteristics
                # Lower value means higher similarity (closer to 0)
                return score < 0.3
        except Exception as e:
            print(f"Error in similarity check: {e}")
    
    return False

# Function to retrieve images from SQLite - retrieve only top 2 most relevant
def get_images_from_db(sources, page_numbers, limit=2):
    if not sources or not page_numbers or not is_manual_related_query(st.session_state.get("current_query", "")):
        return []
    
    try:
        conn = sqlite3.connect(IMAGE_DB_PATH)
        cursor = conn.cursor()
        images = []
        
        # Combine sources and pages for deduplication
        unique_pairs = list(dict.fromkeys(zip(sources, page_numbers)))  # Remove duplicates
        print(unique_pairs)
        # Get images for top relevant pairs (up to the limit)
        for source, page in unique_pairs:
            print(f"SOURCE ----------------------------- {source}")
            print(f"IMAGES ----------------------------- {page}")
            cursor.execute("SELECT image FROM images WHERE pdf_name = ? AND page_num = ?", 
                          (source, page))
            results = cursor.fetchall()
            #print('These are the results')
            for img_data in results:
                if img_data and img_data[0]:
                    cursor.execute("SELECT pdf_link FROM images WHERE pdf_name = ? AND page_num = ?", (source, page))
                    link, *_ = cursor.fetchone()
                    print(f"LINK {link}")
                    images.append((img_data[0], source, page, link))
                    #print(images)
                    if len(images) >= limit:  # Stop retrieving images once the limit is reached
                        conn.close()
                        return images
        
        conn.close()
        return images
    except Exception as e:
        print(f"Error retrieving images: {e}")
        return []

# Reset conversation
def reset_conversation():
    st.session_state.pop('chat_history')
    st.session_state['chat_history'] = [
        {"role":"assistant", "content":"Hey there! How can I assist you today?"}
    ]




def rag_qa_chain(question, retriever, chat_history):
    #llm = ChatGroq(model="mixtral-8x7b-32768", verbose=False)
    llm = ChatOpenAI(model='gpt-4o-2024-08-06')
    output_parser = StrOutputParser()

    contextualize_q_system_prompt = """Given a chat history and the latest user question which might reference context in the chat history,
    formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    
    contextualize_q_chain = contextualize_q_prompt | llm | output_parser

    qa_system_prompt =  """You are a specialized Q&A generation agent focusing on creating questions and answers about the game. Your purpose is to generate training data for model fine-tuning.

    Important Guidelines:
    1. Only generate Q&A pairs based on information explicitly present in the provided context
    2. Format output as plain sentences with questions and answers on separate lines
    3. Do not use any prefixes or labels (Q:, A:, Question:, etc.)
    4. Do not use separators (---, === or similar)
    5. Always include the game name in each question
    6. Focus on technical details including:
       - Troubleshooting procedures
       - Part numbers and specifications
       - Error codes and their resolution
       - Update procedures
       - Game settings and configurations
       - Maintenance requirements
       - Safety guidelines

    Example Format:
    What is the part number for the Marquee plate L in "game_name"?
    The part number for the Marquee plate L on "game_name" is B145-0105-00

    What are the options in the Main Menu of "game_name"?
    The options in the Main Menu of "game_name"are: Game Version, IO Version, Machine ID, IO Board ID, Back

    I just give you the example like how to show the output change the game name word with actual game name when it gives you.
    
    If you can't answer the question ONLY respond with something like 'Here, this might help answer your question'
    

    Retrieved Game Manual Content:
    ------------
    {context}
    ------------
    """
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    final_llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    rag_chain = (
        RunnablePassthrough.assign(
            context=contextualize_q_chain | retriever | format_docs
        )
        | prompt
        | final_llm
        | output_parser
    )
    
    return rag_chain.stream({"question": question, "chat_history": chat_history})

# UI Layout
col1, col2 = st.columns([1, 5])

# Displaying chat history
for message in st.session_state.chat_history:
    avatar = "assets/male.png" if message["role"] == "user" else "assets/bot.png"
    
    with col2:
        st.chat_message(message["role"], avatar=avatar).write(message["content"])

with col1:
    st.button("Reset", use_container_width=True, on_click=reset_conversation)

query = st.chat_input('Enter your message')

if query:
    print("storing Query")
    # Store current query for image relevance check
    st.session_state["current_query"] = query
    
    with col2:
        user_msg = st.chat_message("user", avatar="assets/male.png")
        user_msg.write(query)
    
    st.session_state.chat_history.append({'role': 'user', 'content': query})

    try:
        print('inserting chat msg')
        with col2:
            assistant_msg = st.chat_message("assistant", avatar="assets/bot.png")
            # Use k=3 for retrieval to get more potential context
            response = assistant_msg.write_stream(rag_qa_chain(
                question=query,
                retriever=st.session_state["vectorstore"].as_retriever(search_kwargs={"k": 3}),
                chat_history=st.session_state.chat_history
            ))
            print(response)
        # Only display images for manual-related queries
        if is_manual_related_query(query):
            print("retrieving top 4 image results")
            # Retrieve top documents for image extraction
            retrieved_docs = st.session_state["vectorstore"].as_retriever(search_kwargs={"k": 4}).invoke(query)
            print(retrieved_docs)
            with open('results.txt', 'w', encoding='utf-8')as f:
             f.write(f"{retrieved_docs}")
            # Extract sources and page numbers
            retrieved_sources = [doc.metadata.get("source", "") for doc in retrieved_docs]
            retrieved_pages = [int(doc.metadata.get("page", 0)) for doc in retrieved_docs]
            
            # Get image binary data (limited to top 2)
            image_data_list = get_images_from_db(retrieved_sources, retrieved_pages, limit=1)
            
            # Display images if any were found
            print("we found images")
            if image_data_list:
                st.write("### Relevant Images:")
                for img_data, source, page, link in image_data_list:
                    try:
                        image = Image.open(io.BytesIO(img_data))
                        st.image(image, caption=f"From {source}, Page {page} \n link: {link}", use_container_width=True)
                    except Exception as e:
                        print(f"Error displaying image: {e}")
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        print(f"Error: {e}")
