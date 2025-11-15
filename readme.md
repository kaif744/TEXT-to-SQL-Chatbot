🤖 Text-to-SQL RAG Chatbot

This project is a fully interactive web application that allows non-technical users to ask questions about a database in natural language. It uses a Retrieval-Augmented Generation (RAG) agent to convert user questions into executable SQL queries, fetch the results, and provide a clean, plain-English answer.

The frontend is built with Streamlit, and the backend logic uses LangChain and Google's Gemini LLM.

$$Click here to add your own screenshot\!$$


(Run your app, take a screenshot, and drag-and-drop it onto this README in the GitHub editor)

✨ Features

Natural Language to SQL: Ask questions like "What was the total line total for Jaxbean Group?" instead of writing complex SQL.

Interactive Chat UI: A clean, real-time chat interface built with Streamlit.

RAG Pipeline: The app uses a prompt-engineered chain (LCEL) to generate accurate SQL based on the database's schema.

Secure: All API keys and database credentials are securely managed using Streamlit's secrets management.

📂 Project Structure

This is the structure of the project folder:

Text_to_sqlApp/
├── .streamlit/
│   └── secrets.toml    <- (This file is NOT on GitHub, you must create it)
├── app.py              <- The main Streamlit application
├── requirements.txt    <- All Python libraries needed to run the app
├── .gitignore          <- Tells Git to ignore secrets and venv
└── README.md           <- You are reading this!


🛠️ How to Set Up and Run Locally

Follow these steps to run the project on your own machine.

1. Prerequisites

Python 3.10+

A running PostgreSQL database (this project was built to connect to a local instance)

A Google AI Studio API Key (for the Gemini model)

2. Clone the Repository

# Replace with your GitHub repo URL
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME


3. Set Up a Virtual Environment

# Create the virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate


4. Install Dependencies

pip install -r requirements.txt


5. Create Your Secrets File

You must create a local secrets file to store your credentials.

# 1. Create the folder
mkdir .streamlit

# 2. Create the secrets file (for Windows)
copy NUL .streamlit\secrets.toml

# 2. Create the secrets file (for macOS/Linux)
touch .streamlit/secrets.toml


Now, open the .streamlit/secrets.toml file and add your credentials in this format:

# .streamlit/secrets.toml

DB_PASSWORD = "YOUR_DATABASE_PASSWORD"
GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"


6. Run the App

Make sure your PostgreSQL database is running, then launch the Streamlit app:

streamlit run app.py


Your browser will automatically open, and you can start chatting with your database!
