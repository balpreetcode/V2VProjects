# ##### handling multiple calls, one after the other
# # # # # Speech to text DEEPGRAM
# ### Transcription should not be empty

# import os
# import asyncio
# import json
# import pyaudio
# import websockets
# from dotenv import load_dotenv
# import pyautogui as pg

# # Load environment variables from .env file for secure access
# load_dotenv()

# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 16000
# CHUNK = 8000

# class Transcriber:
#     def __init__(self):
#         self.audio_queue = asyncio.Queue()
#         self.stream = None  # Placeholder for the PyAudio stream
#         self.stop_pushing = False  # Flag to stop pushing data to the queue

#     def mic_callback(self, input_data, frame_count, time_info, status_flag):
#         if not self.stop_pushing:
#             # print("Pushing data to the queue")
#             self.audio_queue.put_nowait(input_data)
#         return (input_data, pyaudio.paContinue)

#     async def sender(self, ws, timeout=0.1):
#         """Send audio data from the microphone to Deepgram."""
#         try:
#             while not self.stop_pushing:  # Check the flag
#                 mic_data = await asyncio.wait_for(self.audio_queue.get(), timeout)
#                 await ws.send(mic_data)
#         except asyncio.TimeoutError:
#             # print("Sender coroutine timed out. Closing...")
#             self.stop_pushing = True  # Set the flag
#             await ws.close()
#             return
#         except websockets.exceptions.ConnectionClosedOK:
#             await ws.send(json.dumps({"type": "CloseStream"}))

#     async def receiver(self, ws):
#         """Receive transcription results from Deepgram."""
#         try:
#             async for msg in ws:
#                 # print("Received message from WebSocket")
#                 res = json.loads(msg)
#                 if res.get("is_final"):
#                     transcript = (
#                         res.get("channel", {})
#                         .get("alternatives", [{}])[0]
#                         .get("transcript", "")
#                     )
#                     # Check if the transcript is empty or not
#                     if transcript.strip():  
#                         print("Transcript:", transcript)
#                         self.stop_pushing = True  # Set the flag to stop pushing data to the queue
#                         return transcript
#         except asyncio.TimeoutError:
#             # print("Receiver coroutine timed out. Stopping...")
#             await ws.close()
#             return None


#     async def run(self, key):
#         deepgram_url = f"wss://api.deepgram.com/v1/listen?punctuate=true&encoding=linear16&sample_rate=16000"
        
#         # Open the microphone stream
#         p = pyaudio.PyAudio()
#         # self.stream = p.open(format=FORMAT, channels=1, rate=16000, input=True, input_device_index=11, stream_callback=self.mic_callback)
#         self.stream = p.open(format=FORMAT, channels=1, rate=16000, input=True, stream_callback=self.mic_callback)
#         self.stream.start_stream()
        
#         async with websockets.connect(
#             deepgram_url, 
#             extra_headers={"Authorization": "Token {}".format(key)}, 
#             timeout=0.3  # added timeout here
#         ) as ws:
            
#             # Launch sender and receiver coroutines
#             sender_coroutine = self.sender(ws)
#             receiver_coroutine = self.receiver(ws)

#             # Collect results (assuming you return the transcript from the receiver)
#             _, transcript = await asyncio.gather(sender_coroutine, receiver_coroutine)
            
#             # Stop the microphone stream
#             self.stream.stop_stream()
#             self.stream.close()
#             p.terminate()
#             print(transcript)
#             return transcript
#     def stop(self):
#         """Stop the transcription."""
#         self.stop_pushing = True
#         if self.stream and not self.stream.is_stopped():
#             self.stream.stop_stream()
#             self.stream.close()
#             self.stream = None

# async def check_end_call(transcriber, check_interval=1):
#     """Asynchronously check for the end call button."""
#     while True:
#         end_call = pg.locateOnScreen("assets/buttons/end_call.png", confidence=0.98)
#         if end_call:
#             print("Call ended")
#             transcriber.stop()  # Stop the transcription
#             return
#         await asyncio.sleep(check_interval)  # Wait for the specified interval before checking again


# def transcribe_stream():
#     DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
#     if DEEPGRAM_API_KEY is None:
#         print("Please set the DEEPGRAM_API_KEY environment variable.")
#         return

#     print("Start speaking...")
#     transcriber = Transcriber()
    
#     loop = asyncio.get_event_loop()  # Use an existing loop if available, otherwise create a new one
#     transcript = loop.run_until_complete(transcriber.run(DEEPGRAM_API_KEY))
#     return transcript

#######################################################################################################


# # # # Speech to text DEEPGRAM
### Transcription should not be empty

# import os
# import asyncio
# import json
# import pyaudio
# import websockets
# from dotenv import load_dotenv
# import pyautogui as pg  # Ensure pyautogui is imported

# # Load environment variables from .env file for secure access
# load_dotenv()

# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 16000
# CHUNK = 8000

# class Transcriber:
#     def __init__(self):
#         self.audio_queue = asyncio.Queue()
#         self.stream = None  # Placeholder for the PyAudio stream
#         self.stop_pushing = False  # Flag to stop pushing data to the queue

#     def mic_callback(self, input_data, frame_count, time_info, status_flag):
#         if not self.stop_pushing:
#             self.audio_queue.put_nowait(input_data)
#         return (input_data, pyaudio.paContinue)

#     async def sender(self, ws, timeout=0.1):
#         """Send audio data from the microphone to Deepgram."""
#         try:
#             while not self.stop_pushing:  # Check the flag
#                 mic_data = await asyncio.wait_for(self.audio_queue.get(), timeout)
#                 await ws.send(mic_data)
#         except asyncio.TimeoutError:
#             self.stop_pushing = True  # Set the flag
#             await ws.close()
#             return
#         except websockets.exceptions.ConnectionClosedOK:
#             await ws.send(json.dumps({"type": "CloseStream"}))

#     # async def receiver(self, ws):
#     #     """Receive transcription results from Deepgram."""
#     #     try:
#     #         async for msg in ws:
#     #             res = json.loads(msg)
#     #             if res.get("is_final"):
#     #                 transcript = (
#     #                     res.get("channel", {})
#     #                     .get("alternatives", [{}])[0]
#     #                     .get("transcript", "")
#     #                 )
#     #                 if transcript.strip():  
#     #                     self.stop_pushing = True  # Set the flag to stop pushing data to the queue
#     #                     return transcript
#     #     except asyncio.TimeoutError:
#     #         await ws.close()
#     #         return None
#     async def receiver(self, ws):
#         """Receive transcription results from Deepgram."""
#         try:
#             async for msg in ws:
#                 res = json.loads(msg)
#                 if res.get("is_final"):
#                     transcript = (
#                         res.get("channel", {})
#                         .get("alternatives", [{}])[0]
#                         .get("transcript", "")
#                     )
#                     if transcript.strip():  
#                         self.transcript = transcript  # Update the transcript attribute
#                         self.stop_pushing = True  # Set the flag to stop pushing data to the queue
#                         return
#         except asyncio.TimeoutError:
#             await ws.close()
#             return


#     def check_call_end(self):
#         """Check for the call end button."""
#         end_call = pg.locateOnScreen("assets/buttons/end_call.png", confidence=0.98)
#         if end_call:
#             print("Call ended")
#             self.stop_pushing = True

#     async def check_call_end_periodically(self, check_interval=1):
#         """Periodically check for the call end button."""
#         while not self.stop_pushing:
#             self.check_call_end()
#             await asyncio.sleep(check_interval)

#     async def run(self, key):
#         deepgram_url = f"wss://api.deepgram.com/v1/listen?punctuate=true&encoding=linear16&sample_rate=16000"
        
#         self.transcript = None  
#         # Open the microphone stream
#         p = pyaudio.PyAudio()
#         self.stream = p.open(format=FORMAT, channels=1, rate=16000, input=True, stream_callback=self.mic_callback)
#         self.stream.start_stream()
        
#         # async with websockets.connect(
#         #     deepgram_url, 
#         #     extra_headers={"Authorization": "Token {}".format(key)}, 
#         #     timeout=0.3
#         # ) as ws:
            
#         #     # Launch sender, receiver, and call end check coroutines
#         #     sender_coroutine = self.sender(ws)
#         #     receiver_coroutine = self.receiver(ws)
#         #     call_end_check_task = asyncio.create_task(self.check_call_end_periodically())

#         #     # Collect results
#         #     _, transcript = await asyncio.gather(sender_coroutine, receiver_coroutine, call_end_check_task)
            
#         #     # Stop the microphone stream
#         #     self.stream.stop_stream()
#         #     self.stream.close()
#         #     p.terminate()
#         #     return transcript
#         # async with websockets.connect(
#         #     deepgram_url, 
#         #     extra_headers={"Authorization": "Token {}".format(key)}, 
#         #     timeout=0.3
#         # ) as ws:

#         #     # Launch sender, receiver, and call end check coroutines
#         #     sender_coroutine = self.sender(ws)
#         #     receiver_coroutine = self.receiver(ws)
#         #     call_end_check_task = asyncio.create_task(self.check_call_end_periodically())

#         #     # Collect results
#         #     results = await asyncio.gather(sender_coroutine, receiver_coroutine, call_end_check_task)
            
#         #     # The transcript is the result of the receiver_coroutine, which is the second in the gather call
#         #     transcript = results[1]
            
#         #     # Stop the microphone stream
#         #     self.stream.stop_stream()
#         #     self.stream.close()
#         #     p.terminate()
#         #     return transcript

#         async with websockets.connect(
#             deepgram_url, 
#             extra_headers={"Authorization": "Token {}".format(key)}, 
#             timeout=0.3
#         ) as ws:

#             # Launch sender, receiver, and call end check coroutines
#             sender_coroutine = self.sender(ws)
#             receiver_coroutine = self.receiver(ws)
#             call_end_check_task = asyncio.create_task(self.check_call_end_periodically())

#             # Collect results
#             await asyncio.gather(sender_coroutine, receiver_coroutine, call_end_check_task)

#             # Stop the microphone stream
#             self.stream.stop_stream()
#             self.stream.close()
#             p.terminate()

#             # Return 'exit' if the call ended, else return the transcript
#             return 'exit' if self.stop_pushing else self.transcript

# def transcribe_stream():
#     DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
#     if DEEPGRAM_API_KEY is None:
#         print("Please set the DEEPGRAM_API_KEY environment variable.")
#         return

#     print("Start speaking...")
#     transcriber = Transcriber()
    
#     loop = asyncio.get_event_loop()
#     transcript = loop.run_until_complete(transcriber.run(DEEPGRAM_API_KEY))

#     # Handle the 'exit' case
#     if transcript == 'exit':
#         return 'exit'
    
#     return transcript

#####################################################################
import os
import asyncio
import json
import pyaudio
import websockets
from dotenv import load_dotenv
import pyautogui as pg  # Ensure pyautogui is imported

# Load environment variables from .env file for secure access
load_dotenv()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8000

class Transcriber:
    def __init__(self):
        self.audio_queue = asyncio.Queue()
        self.stream = None  # Placeholder for the PyAudio stream
        self.stop_pushing = False  # Flag to stop pushing data to the queue
        self.call_end_detected = False

    def mic_callback(self, input_data, frame_count, time_info, status_flag):
        if not self.stop_pushing:
            self.audio_queue.put_nowait(input_data)
        return (input_data, pyaudio.paContinue)

    async def sender(self, ws, timeout=0.1):
        """Send audio data from the microphone to Deepgram."""
        try:
            while not self.stop_pushing:  # Check the flag
                mic_data = await asyncio.wait_for(self.audio_queue.get(), timeout)
                await ws.send(mic_data)
        except asyncio.TimeoutError:
            self.stop_pushing = True  # Set the flag
            await ws.close()
            return
        except websockets.exceptions.ConnectionClosedOK:
            await ws.send(json.dumps({"type": "CloseStream"}))

    # async def receiver(self, ws):
    #     """Receive transcription results from Deepgram."""
    #     try:
    #         async for msg in ws:
    #             res = json.loads(msg)
    #             if res.get("is_final"):
    #                 transcript = (
    #                     res.get("channel", {})
    #                     .get("alternatives", [{}])[0]
    #                     .get("transcript", "")
    #                 )
    #                 if transcript.strip():  
    #                     self.stop_pushing = True  # Set the flag to stop pushing data to the queue
    #                     return transcript
    #     except asyncio.TimeoutError:
    #         await ws.close()
    #         return None
    async def receiver(self, ws):
        """Receive transcription results from Deepgram."""
        try:
            async for msg in ws:
                # Check if the call end button was detected
                if self.call_end_detected:
                    return 'exit'  # Return 'exit' if call end button was detected

                res = json.loads(msg)
                if res.get("is_final"):
                    transcript = (
                        res.get("channel", {})
                        .get("alternatives", [{}])[0]
                        .get("transcript", "")
                    )
                    if transcript.strip():  
                        self.stop_pushing = True
                        return transcript
        except asyncio.TimeoutError:
            await ws.close()
            return None

    # def check_call_end(self):
    #     """Check for the call end button."""
    #     end_call = pg.locateOnScreen("assets/buttons/end_call.png", confidence=0.98)
    #     if end_call:
    #         print("Call ended")
    #         self.stop_pushing = True

    def check_call_end(self):
        """Check for the call end button."""
        end_call = pg.locateOnScreen("assets/buttons/end_call.png", confidence=0.98)
        if end_call:
            print("Call ended")
            self.stop_pushing = True
            self.call_end_detected = True 

    async def check_call_end_periodically(self, check_interval=1):
        """Periodically check for the call end button."""
        while not self.stop_pushing:
            self.check_call_end()
            await asyncio.sleep(check_interval)

    async def run(self, key):
        deepgram_url = f"wss://api.deepgram.com/v1/listen?punctuate=true&encoding=linear16&sample_rate=16000"
        
        # Open the microphone stream
        p = pyaudio.PyAudio()
        self.stream = p.open(format=FORMAT, channels=1, rate=16000, input=True, stream_callback=self.mic_callback)
        self.stream.start_stream()
        
        async with websockets.connect(
            deepgram_url, 
            extra_headers={"Authorization": "Token {}".format(key)}, 
            timeout=0.3
        ) as ws:

            # Launch sender, receiver, and call end check coroutines
            sender_coroutine = self.sender(ws)
            receiver_coroutine = self.receiver(ws)
            call_end_check_task = asyncio.create_task(self.check_call_end_periodically())

            # Collect results
            # results = await asyncio.gather(sender_coroutine, receiver_coroutine, call_end_check_task)
            # results = await asyncio.gather(sender_coroutine, receiver_coroutine, call_end_check_task)
        #     results = await asyncio.gather(sender_coroutine, receiver_coroutine, call_end_check_task)

        # # Check the result of the receiver_coroutine
        #     transcript_or_exit = results[1]
        #     if transcript_or_exit == 'exit':
        #         return 'exit'
            results = await asyncio.gather(sender_coroutine, receiver_coroutine, call_end_check_task)

    # Extract the result of the receiver_coroutine
            transcript_or_exit = results[1]

            # Check if 'exit' should be returned
            if transcript_or_exit == 'exit':
                return 'exit'

            # If 'transcript_or_exit' is not 'exit', it should be the transcript
            # However, we should ensure that it is not None before returning
            if transcript_or_exit is not None:
                return transcript_or_exit

            # If the transcript is None (e.g., due to an error or timeout), you can decide how to handle it.
            # For example, return an empty string, a specific message, or handle the error differently.
            return "No transcript available"
        
        # Check if the call end button was detected
            # if self.call_end_detected:
            #     print("call_end_detected")
            #     return 'exit' 
            # # The transcript is the result of the receiver_coroutine, which is the second in the gather call
            # transcript = results[1]
            
            # Stop the microphone stream
            self.stream.stop_stream()
            self.stream.close()
            p.terminate()
            return transcript


def transcribe_stream():
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
    if DEEPGRAM_API_KEY is None:
        print("Please set the DEEPGRAM_API_KEY environment variable.")
        return

    print("Start speaking...")
    transcriber = Transcriber()
    
    loop = asyncio.get_event_loop()  # Use an existing loop if available, otherwise create a new one
    transcript = loop.run_until_complete(transcriber.run(DEEPGRAM_API_KEY))
    return transcript

####################################
# # # Speech to text DEEPGRAM
## Transcription should not be empty

import os
import asyncio
import json
import pyaudio
import websockets
from dotenv import load_dotenv
import pyautogui as pg  # Ensure pyautogui is imported

# Load environment variables from .env file for secure access
load_dotenv()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8000

class Transcriber:
    def __init__(self):
        self.audio_queue = asyncio.Queue()
        self.stream = None  # Placeholder for the PyAudio stream
        self.stop_pushing = False  # Flag to stop pushing data to the queue

    def mic_callback(self, input_data, frame_count, time_info, status_flag):
        if not self.stop_pushing:
            self.audio_queue.put_nowait(input_data)
        return (input_data, pyaudio.paContinue)

    async def sender(self, ws, timeout=0.1):
        """Send audio data from the microphone to Deepgram."""
        try:
            while not self.stop_pushing:  # Check the flag
                mic_data = await asyncio.wait_for(self.audio_queue.get(), timeout)
                await ws.send(mic_data)
        except asyncio.TimeoutError:
            self.stop_pushing = True  # Set the flag
            await ws.close()
            return
        except websockets.exceptions.ConnectionClosedOK:
            await ws.send(json.dumps({"type": "CloseStream"}))

    async def receiver(self, ws):
        """Receive transcription results from Deepgram."""
        try:
            async for msg in ws:
                res = json.loads(msg)
                if res.get("is_final"):
                    transcript = (
                        res.get("channel", {})
                        .get("alternatives", [{}])[0]
                        .get("transcript", "")
                    )
                    if transcript.strip():  
                        self.stop_pushing = True  # Set the flag to stop pushing data to the queue
                        return transcript
        except asyncio.TimeoutError:
            await ws.close()
            return None

    def check_call_end(self):
        """Check for the call end button."""
        end_call = pg.locateOnScreen("assets/buttons/end_call.png", confidence=0.98)
        if end_call:
            print("Call ended")
            self.stop_pushing = True

    async def check_call_end_periodically(self, check_interval=1):
        """Periodically check for the call end button."""
        while not self.stop_pushing:
            self.check_call_end()
            await asyncio.sleep(check_interval)

    async def run(self, key):
        deepgram_url = f"wss://api.deepgram.com/v1/listen?punctuate=true&encoding=linear16&sample_rate=16000"
        
        # Open the microphone stream
        p = pyaudio.PyAudio()
        self.stream = p.open(format=FORMAT, channels=1, rate=16000, input=True, stream_callback=self.mic_callback)
        self.stream.start_stream()
        
        async with websockets.connect(
            deepgram_url, 
            extra_headers={"Authorization": "Token {}".format(key)}, 
            timeout=0.3
        ) as ws:

            sender_coroutine = self.sender(ws)
            receiver_coroutine = self.receiver(ws)
            call_end_check_task = asyncio.create_task(self.check_call_end_periodically())

            # Wait for either transcription to complete or call to end
            done, pending = await asyncio.wait(
                [sender_coroutine, receiver_coroutine, call_end_check_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel any pending tasks
            for task in pending:
                task.cancel()

            # Extract transcript if available
            transcript = None
            for task in done:
                if task.get_name() == "receiver_coroutine":
                    transcript = task.result()

            # Stop the microphone stream
            self.stream.stop_stream()
            self.stream.close()
            p.terminate()

            return transcript


def transcribe_stream():
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
    if DEEPGRAM_API_KEY is None:
        print("Please set the DEEPGRAM_API_KEY environment variable.")
        return

    print("Start speaking...")
    transcriber = Transcriber()
    
    loop = asyncio.get_event_loop()
    transcript = loop.run_until_complete(transcriber.run(DEEPGRAM_API_KEY))
    return transcript

