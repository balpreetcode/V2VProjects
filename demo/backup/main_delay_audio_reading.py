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

# Load environment variables from .env file
load_dotenv()

# Access environment variables
PPLX_API_KEY = os.environ.get("PPLX_API_KEY")
os.environ["PPLX_API_KEY"] = PPLX_API_KEY

model_name="llama-2-70b-chat"

sys.path.append("./components")
sys.path.append("./constants")
import speech_to_text1
# from filler_mapping import classify_and_play_audio, refresh_learning_data
from dictionary import phrases_dict

def generate_unique_id():
    return str(uuid.uuid4())

conversation_id = generate_unique_id()

# 1. FAISS Indexing
# Convert phrases to embeddings for searching
vectorizer = TfidfVectorizer().fit(phrases_dict.keys())
phrases_embeddings = vectorizer.transform(phrases_dict.keys())
index = faiss.IndexIDMap(faiss.IndexFlatIP(phrases_embeddings.shape[1]))
index.add_with_ids(np.array(phrases_embeddings.toarray(), dtype=np.float32), np.array(list(range(len(phrases_dict)))))

def find_matching_audio(sentence):
    start_time_f = datetime.datetime.now()
    # print(f'Phrase given to faiss {start_time_f}')
    # Convert the sentence to embedding and search in the index
    sentence_embedding = vectorizer.transform([sentence]).toarray().astype(np.float32)
    D, I = index.search(sentence_embedding, 1)
    match_index = I[0][0]
    matching_sentence = list(phrases_dict.keys())[match_index]

    if D[0][0] > 0.1:  # You can adjust this threshold based on desired accuracy
        return phrases_dict[matching_sentence]
    return None

processed_sentences = set()

def handle_gpt_response(full_content):
    # Split content into sentences
    sentences = re.split(r'[.!?]', full_content)
    # print(f'Sentence split: {datetime.datetime.now()}')
    sentences = [s.strip() for s in sentences if s]

    for sentence in sentences:
        # Check if sentence was already processed
        if sentence not in processed_sentences:
            audio_code = find_matching_audio(sentence)
            print(f'sentence sent to faiss : {sentence}')
            if audio_code:
                audio_path = f"./assets/audio_files_pixel/{audio_code}.wav"
                wav_obj = wavio.read(audio_path)
                sd.play(wav_obj.data, samplerate=wav_obj.rate)
                sd.wait()
            # Mark sentence as processed
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

    while True:
        end_call = pg.locateOnScreen("assets/buttons/end_call.png", confidence = 0.98)  # path to your end call button image
        if end_call:
            print("Call ended")
            break
        # query = input('user: ')
        query = speech_to_text1.transcribe_stream()
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

def open_website(url):
        webbrowser.open(url, new=2)  # new=2 opens in a new tab, if possible

# Opening call hipppo dialer
website = 'https://dialer.callhippo.com/dial'
#open_website(website)

#time.sleep(15)
            
while True:  # Main loop for handling incoming calls
    accept = pg.locateOnScreen("assets/buttons/accept.png", confidence=0.9)
    if accept:
        x, y, width, height = accept
        click_x, click_y = x + width // 2, y + height // 2  # Calculate the center of the button
        print("Call received at coordinates:", (click_x, click_y))
        pg.moveTo(click_x, click_y)  # Move to the center of the button
        time.sleep(0.5)  # Short delay
        pg.mouseDown()
        time.sleep(0.1)  # Short delay to simulate a real click
        pg.mouseUp()
        print("Call accepted")
        chat_with_user()  # Start chat with user

        print("Waiting for next call...")
        time.sleep(5)
    else:
        print("No call detected.")
        time.sleep(5)        
