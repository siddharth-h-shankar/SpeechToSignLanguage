#!/usr/bin/env python
# coding: utf-8
# Installing widgets for button creation
# In[7]:


#get_ipython().run_line_magic('pip', 'install ipywidgets')

# Creating buttons for Live recording + transcribing and stop# Creating threads for 2 tasks : 
#    1. Recording audio
#    2. Transcribing live audio
    
#  This is done so that these 2 tasks run in background without any interruption of main function
# In[22]:


import ipywidgets as widgets
from IPython.display import display
from queue import Queue
from threading import Thread

messages = Queue()
recordings = Queue()

record_button = widgets.Button(
    description='Record',
    disabled=False,
    button_style='success',
    tooltip='Record',
    icon='microphone'
)

stop_button = widgets.Button(
    description='Stop',
    disabled=False,
    button_style='warning',
    tooltip='Stop',
    icon='stop'
)

output = widgets.Output()

def start_recording(data):
    messages.put(True)
    
    with output:
        display("Starting...")
        record = Thread(target=record_microphone(5))
        record.start()
        transcribe = Thread(target=speech_recognition, args=(output,))
        transcribe.start()

def stop_recording(data):
    with output:
        messages.get()
        display("Stopped.")
    
record_button.on_click(start_recording)
stop_button.on_click(stop_recording)

display(record_button, stop_button, output)

# Installing pyaudio for recording audio
# In[9]:


#get_ipython().run_line_magic('pip', 'install pyaudio')


# In[10]:


import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))

p.terminate()


# In[17]:


CHANNELS = 1
FRAME_RATE = 16000
RECORD_SECONDS = 20
AUDIO_FORMAT = pyaudio.paInt16
SAMPLE_SIZE = 2

def record_microphone(chunk=1024):
    p = pyaudio.PyAudio()

    stream = p.open(format=AUDIO_FORMAT,
                    channels=CHANNELS,
                    rate=FRAME_RATE,
                    input=True,
                    input_device_index=1,
                    frames_per_buffer=chunk)

    frames = []

    while not messages.empty():
        data = stream.read(chunk)
        frames.append(data)
        if len(frames) >= (FRAME_RATE * RECORD_SECONDS) / chunk:
            recordings.put(frames.copy())
            frames = []

    stream.stop_stream()
    stream.close()
    p.terminate()


# In[12]:


#get_ipython().run_line_magic('pip', 'install vosk')


# In[13]:


#get_ipython().run_line_magic('pip', 'install transformers')


# In[14]:


#get_ipython().run_line_magic('pip', 'install torch')


# In[15]:


import subprocess
import json
from vosk import Model, KaldiRecognizer
import time

model = Model(model_name="vosk-model-en-us-0.22")
rec = KaldiRecognizer(model, FRAME_RATE)
rec.SetWords(True)
    
def speech_recognition(output):
    
    while not messages.empty():
        frames = recordings.get()
        
        rec.AcceptWaveform(b''.join(frames))
        result = rec.Result()
        text = json.loads(result)["text"]


# In[ ]:




