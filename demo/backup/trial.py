## main7.py
## handling subsequent calls , also during transcription but after a gap of 10- 12 seconds.
## integrated whatsapp automation

## Lowest latency, no mongo db connection, streamed answer is sent to faiss
import os
import uuid
import datetime
import openai
from dotenv import load_dotenv
import numpy as np
import faiss
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
import sounddevice as sd
import wavio
import re
import time
import pyautogui as pg
import webbrowser

time.sleep(3)
            
while True:  # Main loop for handling incoming calls
    accept = pg.locateOnScreen("assets/buttons/end_call.png", confidence=0.98)
    if accept:
        print("Call ended")
        chat_with_user()  # Start chat with user

        # After chat_with_user returns, wait for the next call
        print("Waiting ")
        time.sleep(5)  # Wait time before checking for the next call, adjust as needed
    else:
        print("No call end detected.")
        time.sleep(5)  # Sleep if no call is detected
