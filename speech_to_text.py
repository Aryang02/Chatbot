import sys
from logger import logging
import speech_recognition as sr
from exception import CustomException

r = sr.Recognizer()

def record_text():
    try:
        with sr.Microphone() as source2:
            r.adjust_for_ambient_noise(source2, duration=0.3)
            audio2 = r.listen(source2, timeout=5, phrase_time_limit=10)
            MyText = r.recognize_google(audio2)
            return MyText
    except sr.RequestError as e:
        logging.info("Couldn't request results; {0}".format(e))
        raise CustomException(e, sys)
    except sr.UnknownValueError as e:
        logging.info("Unknown error occured")
        raise CustomException(e, sys)

def output_text(text):
  with open("output_text.txt", "a") as f:
    f.write(text)
    f.write("\n")
  return


def voice_rec():
    text = record_text()
    logging.info("Voice Query Recorded")
    return text
