import streamlit as st
import urllib.parse
import re

# --- Core LangChain and Database Imports ---
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

# =============================================================================
# 1. DATABASE AND LLM INITIALIZATION (No changes here)
# =============================================================================

@st.cache_resource
def get_db_connection():
    """Connects to the PostgreSQL database and returns the db object."""
    try:
        host = 'localhost'
        port = '5432'
        username = 'postgres'
        # --- READ FROM SECRETS ---
        password = st.secrets["DB_PASSWORD"]
        database_schema = 'text_to_sql'
        
        encoded_password = urllib.parse.quote_plus(password)
        postgresql_uri = f"postgresql+psycopg2://{username}:{encoded_password}@{host}:{port}/{database_schema}"
        
        db = SQLDatabase.from_uri(postgresql_uri, sample_rows_in_table_info=2)
        print("Database connected successfully!")
        return db
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        print(f"Error connecting to database: {e}")
        return None

@st.cache_resource
def get_llm():
    """Initializes the Gemini LLM."""
    try:
        # --- READ FROM SECRETS ---
        llm = ChatGoogleGenerativeAI(
            model='gemini-2.0-flash', 
            api_key=st.secrets["GOOGLE_API_KEY"] 
        )
        return llm
    except Exception as e:
        st.error(f"Error initializing LLM: {e}")
        print(f"Error initializing LLM: {e}")
        return None

@st.cache_resource
def get_sql_chain(_db, _llm):
    """Creates the SQL generation chain (your exact logic)."""
    
    def get_schema(db):
        return db.get_table_info()

    # Your prompt template from the notebook
    template = """Based on the table schema below, Write a sql query that will answer the user's question:
Remember : only provide me the sql query dont add anything else. provide me sql query in a single line dont add line breaks 
Table Schema : {schema}
Question : {question}
sql query:
"""
    prompt = ChatPromptTemplate.from_template(template)
    
    # Your LCEL chain from the notebook
    sql_chain = (
        RunnablePassthrough.assign(schema=lambda _: get_schema(_db))
        | prompt
        | _llm.bind(stop=["\nSQLResult:"])
        | StrOutputParser()
    )
    return sql_chain

# =============================================================================
# 2. FULL RAG CHAIN (Text -> SQL -> Result -> Text)
#    *** THIS FUNCTION HAS BEEN FIXED ***
# =============================================================================

def get_full_response(user_question: str, db: SQLDatabase, llm: ChatGoogleGenerativeAI, sql_chain):
    """
    Takes a user question and returns a natural language response.
    1. Generates SQL query.
    2. Extracts and cleans SQL query.
    3. Executes SQL query.
    4. Generates natural language answer from the SQL result.
    """
    
    # --- Step 1: Generate SQL Query ---
    sql_query_response = sql_chain.invoke({"question": user_question})
    print(f"Raw LLM SQL Response: {sql_query_response}")
    
    # --- Step 2: Extract SQL Query (FIXED LOGIC) ---
    sql_query = ""
    
    # Try to find the query inside markdown backticks
    # This regex: r"```sql\s*(.*?)\s*```" has one capture group (.*?)
    query_match_markdown = re.search(r"```sql\s*(.*?)\s*```", sql_query_response, re.DOTALL | re.IGNORECASE)
    
    if query_match_markdown:
        # If markdown is found, use group(1) to get the clean query
        sql_query = query_match_markdown.group(1).strip()
        print(f"Extracted SQL (from markdown): {sql_query}")
    else:
        # If no markdown, try to find a plain SELECT statement
        # This regex: r"(SELECT.*?;)" has one capture group (SELECT...;)
        query_match_plain = re.search(r"(SELECT.*?;)", sql_query_response, re.DOTALL | re.IGNORECASE)
        if query_match_plain:
            # If plain query is found, use group(1)
            sql_query = query_match_plain.group(1).strip()
            print(f"Extracted SQL (plain): {sql_query}")
        else:
            # If no SQL is found at all, the LLM might be answering directly
            if "SELECT" not in sql_query_response.upper():
                  print("No SQL found, returning direct answer.")
                  return sql_query_response # e.g., "Sorry, I can't answer that."
            
            print(f"Failed to extract query from: {sql_query_response}")
            return "I'm sorry, I couldn't generate a valid SQL query for that question."
    
    # Ensure it ends with a semicolon for valid SQL
    if not sql_query.endswith(';'):
        sql_query += ';'
        
    print(f"Final SQL Query to run: {sql_query}")
    
    # --- Step 3: Execute SQL Query ---
    try:
        sql_result = db.run(sql_query)
        print(f"SQL Result: {sql_result}")
    except Exception as e:
        print(f"Error running query: {e}")
        return f"I encountered an error while running the query. Error: {e}"

    # --- Step 4: NEW - Generate Natural Language Response ---
    answer_template = """
    A user asked a question, and an SQL query was generated and executed.
    Now, provide a clean, natural language answer based on the query and its result.
    
    Original Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    
    Final Answer (in plain English):
    """
    answer_prompt = ChatPromptTemplate.from_template(answer_template)
    
    answer_chain = (
        answer_prompt
        | llm
        | StrOutputParser()
    )
    
    final_answer = answer_chain.invoke({
        "question": user_question,
        "query": sql_query,
        "result": sql_result
    })
    
    return final_answer

# =============================================================================
# 3. STREAMLIT CHAT UI (No changes here)
# =============================================================================

st.set_page_config(page_title="Text-to-SQL Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Text-to-SQL RAG Chatbot")
st.caption("Ask me anything about your database!")

# --- Load all the components ---
try:
    db = get_db_connection()
    llm = get_llm()
    if db and llm:
        sql_chain = get_sql_chain(db, llm)
    else:
        st.error("Failed to initialize database or LLM connection. Please check secrets.")
        st.stop()
except Exception as e:
    st.error(f"Failed to initialize the application components: {e}")
    st.stop()


# --- Chat History Management ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! How can I help you with your database today?"}
    ]

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input and Response Logic ---
if prompt := st.chat_input("What is the total 'Line Total' for Jaxbean Group?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your request..."):
            response = get_full_response(prompt, db, llm, sql_chain)
            st.markdown(response)
            
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})