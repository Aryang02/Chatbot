import re
import sys
import nltk
import chromadb
from apikey import apikey
from logger import logging
from nltk.corpus import stopwords
from exception import CustomException
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from langchain_google_genai import ChatGoogleGenerativeAI
from llama_index.core import SimpleDirectoryReader
import chromadb.utils.embedding_functions as embedding_functions

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

logging.info("In data collection")

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
db = chromadb.PersistentClient(path="./chroma_db")
google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=apikey)
collection = db.get_or_create_collection("Testing", embedding_function=google_ef)
llmmodel = ChatGoogleGenerativeAI(model='gemini-pro', temperature=0.6, google_api_key=apikey)


def store_pdfs(pdf_docs):
  for files in pdf_docs:
    with open(f"./data/{files.name}", "wb") as pdf_file:
        pdf_file.write(files.getbuffer())

def process_and_transform(text):
    text = "".join(re.findall(r".*", text, re.DOTALL))
    with open("processed_text.txt", "w", encoding='utf-8') as f:
        f.write("".join(text))
    text = text.lower()

    words = word_tokenize(text)
    processed_words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]

    return "".join(processed_words)

def get_ids(docs):
    ids = [f"id_{i}" for i in range(1, len(docs)+1)]
    return ids

def create_index(pdf_docs=None):
    try:
        if pdf_docs:
            store_pdfs(pdf_docs)

        documents = SimpleDirectoryReader("./data").load_data()
        logging.info("All documents retrieved")
        processed_docs = [process_and_transform(doc.get_content()) for doc in documents]
        logging.info("Documents processed")
        ids = get_ids(processed_docs)
        logging.info("Document ids generated")
        collection.add(
            documents=processed_docs,
            ids=ids,
        )
        logging.info("Vector Index Created and Stored")

    except Exception as e:
        logging.info("Error in data collection")
        raise CustomException(e, sys)

