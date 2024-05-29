import os
import sys
import argparse
import chromadb
from logger import logging
from exception import CustomException
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import chromadb.utils.embedding_functions as embedding_functions
from langchain.chains.conversation.memory import ConversationBufferMemory

apikey = os.getenv("GOOGLE_API_KEY")
llmmodel = ChatGoogleGenerativeAI(
    model="gemini-pro", temperature=0.6, convert_system_message_to_human=True
)
google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=apikey)
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("quickstart", embedding_function=google_ef)
logging.info("Chroma client created")
chat_history = []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="prompt for conversation")
    parser.add_argument(
        "--prompt", type=str, help="user input for conversation", required=True
    )
    args = parser.parse_args()
    logging.info("Prompt Parsed:", {args.prompt}) 
    context = chroma_collection.query(
      query_texts=[args.prompt],
      n_results=5,
    )
    logging.info(f"Context Generated")
    template = """Answer the question based only on the following context and previous conversation:
    {context}
    {previous_conversation}
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    logging.info("Prompt Generated")
    try:
        logging.info(f"Loading qa chain with prompt: {args.prompt}")
        output_parser = StrOutputParser()
        chain = prompt | llmmodel | output_parser
        logging.info("Loading chain completed")
        response = chain.invoke({"context": context,"previous_conversation": chat_history, "question": args.prompt})
        logging.info("Response generated")
        chat_history.append(("You:", args.prompt))
        chat_history.append(("Bot:", response))
        logging.info("Chat history updated")
        logging.info("Response saved", response)
        print(response)
        logging.info("Response sent")
    except Exception as e:
        raise CustomException(e, sys)
