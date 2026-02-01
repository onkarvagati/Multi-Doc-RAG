import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationalRetrievalChain
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from datetime import datetime
import tempfile
import time


# pdf extraction

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text


# text splitting

def get_text_chunks(raw_text):
    text_splitter = CharacterTextSplitter(
        separator="\n", 
        chunk_size=3000,
        chunk_overlap=400,
        length_function=len
    )
    return text_splitter.split_text(raw_text)


# vector store

def get_vectorstore(text_chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return FAISS.from_texts(texts=text_chunks, embedding=embeddings)

# conversation chain

def get_conversation_chain(vectorstore):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

def type_writer(text, speed=0.015):
    placeholder = st.empty()
    typed_text = ""

    for char in text:
        typed_text += char
        placeholder.markdown(typed_text)
        time.sleep(speed)

def answer_not_in_docs(answer: str) -> bool:
    triggers = [
        "not mentioned",
        "not available",
        "no information",
        "not found",
        "does not contain",
        "no context",
        "i don't know",
        "not provided"
    ]

    answer_lower = answer.lower()
    return any(t in answer_lower for t in triggers)

def web_search_answer(question: str) -> str:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    prompt = f"""
Search the web and answer the following question accurately.
If needed, use up-to-date information.

Question: {question}
"""

    response = llm.invoke(prompt)
    return response.content
  
  
def handle_userinput(user_question):
    response = st.session_state.conversation.invoke(
        {"question": user_question}
    )

    answer = response["answer"]
    st.session_state.chat_history = response["chat_history"]

    # render chat history
    for message in st.session_state.chat_history[:-1]:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)

    # last assistant message (custom handling)
    with st.chat_message("assistant"):

        if answer_not_in_docs(answer):
            st.markdown(
                "❌ **This question is not available in the uploaded PDF.**\n\n"
                "Would you like me to **search the web and answer it?**"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Yes, search web"):
                    st.session_state.web_mode = True
                    st.session_state.pending_question = user_question
                    st.success("Web search enabled. Ask again ")

            with col2:
                if st.button("❌ No"):
                    st.info("Okay Please upload the correct PDF.")

        else:
            # normal typing animation
            type_writer(answer)



def export_chat_pdf(chat_history):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(
        temp_file.name,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    # title
    story.append(Paragraph("<b>Multi-Doc RAG Chat</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # date and time
    date_str = datetime.now().strftime("%d %B %Y, %I:%M %p")
    story.append(Paragraph(f"<i>Generated on: {date_str}</i>", styles["Normal"]))
    story.append(Spacer(1, 20))

    # Chat messages
    for msg in chat_history:
        if isinstance(msg, HumanMessage):
            role = "<b>Question:</b>"
        else:
            role = "<b>Answer:</b>"

        content = msg.content.replace("\n", "<br/>")
        story.append(Paragraph(f"{role} {content}", styles["BodyText"]))
        story.append(Spacer(1, 14))

    doc.build(story)
    return temp_file.name

def handle_web_chat(user_question):
    with st.chat_message("assistant"):
        type_writer(
            "🌐 **Web mode enabled**\n\n"
            "Answering without PDF context:\n\n"
            f"**Answer:** {user_question}"
        )

    # turn off web mode after one answer
    st.session_state.web_mode = False
    st.session_state.pending_question = None


def main():
    load_dotenv()

    st.set_page_config(page_title="Multi-Doc RAG", page_icon=":books:")
    st.title(":books: Multi-Doc RAG")

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    user_question = st.chat_input("Ask a question about your documents")
    
    if user_question:

    # Case 1: Web mode ON
        if st.session_state.web_mode:
            handle_web_chat(user_question)

    # Case 2: PDF processed → RAG
        elif st.session_state.conversation:
            handle_userinput(user_question)

    # Case 3: Nothing uploaded yet
        else:
            st.warning("⚠️ Please upload and process a PDF first")
   
    if "web_mode" not in st.session_state:
        st.session_state.web_mode = False

    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None
   

    with st.sidebar:
        st.header("Upload Documents:books:")

        pdf_docs = st.file_uploader(
            "Drag and drop files here",
            type=["pdf"],
            accept_multiple_files=True
        )

        if st.button("Process"):
            if not pdf_docs:
                st.warning("Please upload at least one PDF")
            else:
                with st.spinner("Processing documents..."):
                    raw_text = get_pdf_text(pdf_docs)
                    text_chunks = get_text_chunks(raw_text)
                    vectorstore = get_vectorstore(text_chunks)
                    st.session_state.conversation = get_conversation_chain(vectorstore)

                st.success("Documents processed successfully")

        if st.session_state.get("chat_history"):
            st.divider()
            st.subheader("Chat Export")

            pdf_path = export_chat_pdf(st.session_state.chat_history)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Chat (PDF)",
                    data=f,
                    file_name="multi_doc_rag_chat.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    main()
