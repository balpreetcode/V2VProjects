## audio preloaded
## handling subsequent calls , also during transcription but after a gap of 10- 12 seconds.
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
import soundfile as sf
import threading
from queue import Queue

# Load environment variables from .env file
load_dotenv()

# Access environment variables
PPLX_API_KEY = os.environ.get("PPLX_API_KEY")
os.environ["PPLX_API_KEY"] = PPLX_API_KEY
PLAYHT_USER_ID = os.environ.get("PLAYHT_USER_ID")
os.environ["PLAYHT_USER_ID"] = PLAYHT_USER_ID
PLAYHT_API_KEY = os.environ.get("PLAYHT_API_KEY")
os.environ["PLAYHT_API_KEY"] = PLAYHT_API_KEY

model_name="llama-2-70b-chat"

sys.path.append("./components")
sys.path.append("./constants")
import speech_to_text1
# from filler_mapping import classify_and_play_audio, refresh_learning_data
from dictionary import phrases_dict
from stream_audio import stream_text_to_audio


processed_sentences = set()

def handle_gpt_response(full_content):
    sentences = re.split(r'[.!?]', full_content)
    sentences = [s.strip() for s in sentences if s]

    for sentence in sentences:
        if sentence not in processed_sentences:
            stream_text_to_audio(sentence, PLAYHT_API_KEY, PLAYHT_USER_ID) 
            processed_sentences.add(sentence)


def chat_with_user():
    messages = [
        {
            "role": "system",
            "content": (
                "RESPOND WITH A VERY SHORT ANSWER. You are a receptionist named Jacob. Your task is to give demo about the academy to the user who is calling you and answer their queries based on the following information:" 
                "Following is a weekly schedule for Fight Flow Academy, which includes classes for MMA, boxing, and fitness:"
                "Monday to Friday at 6:15 AM: Boxing Bootcamp with Aileen. Kickboxing Bootcamp also appears on some days."
                "Saturday: HIIT Boxing at 8:00 AM and Muay Thai at 9:00 AM with Aileen."
                "Sunday: Muay Thai at 4:30 PM with Daison, and Jiu Jitsu (Gi) at 6 PM with Scott."
                "Evenings throughout the week at 5:30 PM: Various classes, including Youth Boxing/Kickboxing, Muay Thai, and MMA/MT Sparring."
                "Evening classes at 6:30 PM and 7:30 PM: Boxing Bootcamp, Muay Thai, Kickboxing Bootcamp, and Boxing Technique with instructors Sean, Johnny K, Tanner, Hung, and Daniel."
                "Our classes cater to all levels, from beginners to advanced practitioners, ensuring a safe and constructive learning environment. Empower yourself today at Fight Flow Academy in Raleigh!"
                "If the user asks how to register, tell them that you will send the details through SMS and inform them that there is one time registration fees of 50 dollars. If the user shows interest in joining, ask them if they would like to register. If yes, ask for their contact information. If no, thank them for their time."
                "End of the conversation: Have a great day!"
                "The address of Fight Flow Academy is: 900 E Six Forks Road, Raleigh, North Carolina."
                "You are having a conversation. Only respond to the last query in 2 or 3 sentences."
            ),
        }
    ]
    processed_content = ""

    sentence_end_pattern = re.compile(r'(?<=[.?!])\s')
    # global is_audio_playing

    while True:
        end_call = pg.locateOnScreen("assets/buttons/end_call.png", confidence = 0.98)  # path to your end call button image
        if end_call:
            print("Call ended")
            break
          
        query = speech_to_text1.transcribe_stream()
        print(query)
        if query is None:  # Check if the transcription was interrupted
            print("Exiting chat due to call end.")
            break
        if query.lower() == "exit":
            break

        messages.append({"role": "user", "content": query})

        # Chat completion with streaming
        response_stream = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            api_base="https://api.perplexity.ai",
            api_key=PPLX_API_KEY,
            stream=True,
        )

        for response in response_stream:
            if 'choices' in response:
                content = response['choices'][0]['message']['content']
                new_content = content.replace(processed_content, "", 1).strip()  # Remove already processed content
                print(new_content)

                # Split the content by sentence-ending punctuations
                parts = sentence_end_pattern.split(new_content)

                # Process each part that ends with a sentence-ending punctuation
                for part in parts[:-1]:  # Exclude the last part for now
                    part = part.strip()
                    if part:
                        handle_gpt_response(part + '.')  # Re-add the punctuation for processing
                        processed_content += part + ' '  # Add the processed part to processed_content

                # Now handle the last part separately
                last_part = parts[-1].strip()
                if last_part:
                    # If the last part ends with a punctuation, process it directly
                    if sentence_end_pattern.search(last_part):
                        handle_gpt_response(last_part)
                        processed_content += last_part + ' '
                    else:
                        # Otherwise, add it to the sentence buffer to process it later
                        processed_content += last_part + ' '
        if last_part:
            print(f"Processed part sent to FAISS: '{last_part}'")
            handle_gpt_response(last_part)
            processed_content += last_part + ' '

        # Append only the complete assistant's response to messages
        if content.strip():
            messages.append({"role": "assistant", "content": content.strip()})


chat_with_user()
