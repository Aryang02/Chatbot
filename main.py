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

st.set_page_config("Chat with PDFs")
st.header("Chat with PDF using Gemini💁")

if "chat_history" not in st.session_state:
  st.session_state["chat_history"] = []

for message in st.session_state["chat_history"]:
  with st.chat_message(message["role"]):
      st.markdown(message["content"])

user_question = st.chat_input("Ask a Question from the PDF Files")
if user_question:
    st.chat_message("user").markdown(user_question)
    st.session_state["chat_history"].append({"role": "user", "content": user_question})
    res = subprocess.run([path, "model.py", "--prompt", user_question], capture_output = True, text=True)
    st.chat_message("assisstant").markdown(res.stdout)
    st.session_state["chat_history"].append({"role": "assistant", "content": res.stdout})
voice_input = st.button(label="Voice Input")
if voice_input:
    user_question = voice_rec()
    st.chat_message("user").markdown(user_question)
    st.session_state["chat_history"].append({"role": "user", "content": user_question})
    res = subprocess.run([path, "model.py", "--prompt", user_question], capture_output = True, text=True)
    st.chat_message("assistant").markdown(res.stdout)
    st.session_state["chat_history"].append({"role": "assistant", "content": res.stdout})

with st.sidebar:
  st.title("Menu:")
  pdf_docs = st.file_uploader(
      "Upload your PDF Files and Click on the Submit & Process Button",
      accept_multiple_files=True,
  )
  folderid = (st.text_input("Enter drive folder link: ")).split('/')[-1]
  if st.button("Submit & Process"):
    with st.spinner("Processing..."):
      if folderid:
        try:
          subprocess.run([path, "accessdrive.py", "--folderid", folderid], capture_output = False)
          create_index()
        except Exception as e:
          raise CustomException(e, sys)
      elif pdf_docs:
        create_index(pdf_docs)
      st.success("Done")
