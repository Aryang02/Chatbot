import os
import sys
import subprocess
import streamlit as st
from logger import logging
from dotenv import load_dotenv
from speech_to_text import voice_rec
from processdata import create_index
from exception import CustomException

load_dotenv()

apikey = os.getenv("GOOGLE_API_KEY")

path = os.getenv("PATH_TO_PYTHON_SCRIPT")

def output(user_question, res):
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    st.session_state["chat_history"].append(("You:", user_question))
    st.session_state["chat_history"].append(("Bot:", res))

    for role, text in st.session_state["chat_history"]:
        st.write(f"{role} {text}")


if __name__ == "__main__":
  st.set_page_config("Chat with PDFs")
  st.header("Chat with PDF using Gemini💁")

  user_question = st.chat_input("Ask a Question from the PDF Files")
  voice_input = st.button(label="Voice Input")
  if voice_input:
      user_question = voice_rec()
      res = subprocess.run([path, "model.py", "--prompt", user_question], capture_output = True, text=True)
      output(user_question, res.stdout)
  if user_question:
      res = subprocess.run([path, "model.py", "--prompt", user_question], capture_output = True, text=True)
      output(user_question, res.stdout)
  
  with st.sidebar:
    st.title("Menu:")
    pdf_docs = st.file_uploader(
        "Upload your PDF Files and Click on the Submit & Process Button",
        accept_multiple_files=True,
    )
    folderid = ''.join(st.text_input("Enter drive folder link: "))
    if st.button("Submit & Process"):
      with st.spinner("Processing..."):
        if folderid:
          try:
            subprocess.run([path, "accessdrive.py", "--folderid", folderid], capture_output = False)
            create_index()
          except Exception as e:
            raise CustomException(e, sys)
        if pdf_docs:
          create_index(pdf_docs)
        st.success("Done")
