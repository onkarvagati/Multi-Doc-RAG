# Multi-Document RAG Chatbot (PDF + Web Fallback)

A Streamlit-based **Retrieval-Augmented Generation (RAG)** chatbot that allows users to:

- Upload **multiple PDFs**
- Ask questions based on uploaded documents
- Detect when an answer is **not present in the PDFs**
- Ask user permission to **search the web**
- Answer using **Gemini (Google Generative AI)**
- Export chat history as a **PDF**
- Enjoy a **custom chat UI with avatars & CSS**



##  Features

- Multi-PDF upload  
- Chunking + FAISS vector store  
- HuggingFace embeddings  
- Gemini-powered answers  
- Smart fallback when answer not in PDF  
- Web search mode (Gemini output)  
- Yes / No buttons for web search  
- Typing animation  
- Chat export as PDF  
- Custom chat UI (avatars + bubbles)



## Tech Stack

- **Python**
- **Streamlit**
- **LangChain**
- **Google Gemini API**
- **FAISS**
- **HuggingFace Embeddings**
- **PyPDF2**
- **ReportLab**



## Project Structure

project/
│
├── app.py                 # Main Streamlit app
├── html_templates.py      # Chat UI (CSS + HTML templates)
├── README.md              #project documentaion
├── requirements.txt       #python dependancies
├── .env                   # Gemini API key

##  Installation (Local)

```bash
git clone https://github.com/YOUR_USERNAME/multi-doc-rag-chatbot.git
cd multi-doc-rag-chatbot

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt