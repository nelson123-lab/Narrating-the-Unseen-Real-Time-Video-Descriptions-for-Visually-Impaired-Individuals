# Import necessary libraries and modules
import os
from openai import OpenAI
import openai
import base64
import requests
import cv2
import sounddevice as sd
import soundfile as sf
import io
import keyboard
import threading
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI()

# Function to get description for a single image using OpenAI GPT-4 Vision model
def current_frame_descriptions(image):

    # Set headers for API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    # Define payload for API request
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Describe the image. Keep it brief. Don't start with 'The image shows'. Just give the description."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image}"
                        }
                    },
                ]
            }
        ],
        "max_tokens": 300
    }

    # Make API request and return the generated description
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

# Function to get description for two consecutive images with contextual analysis
def continous_frame_descriptions(prev_image, curr_image, preview):
    # Set headers for API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    # Define payload for API request
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""The images are two consecutive frames of a continuous live video. 
                                    The first image is of the previous frame, and the second image is of the current frame.
                                    The description of the previous frame is {preview}.
                                    Compare the two images and also compare the description of both the frames.
                                    Then describe the current frame or anything new comes in the description. 
                                    Don't repeat anything that is already there in the previous frame or {preview}.
                                    Always make a connection between the two frames and between the current description and {preview} 
                                    as these are the images from a continuous live video feed. Don't mention anything about comparison in your final answer.
                                    Just describe the current frame after doing the above analysis. Don't start with 'in this frame'.  Keep it brief."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{prev_image}"}
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{curr_image}"}
                    },
                ]
            }
        ],
        "max_tokens": 300
    }

    # Making API requests and getting the JSON responses.
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response.json()['choices'][0]['message']['content']

# Function to convert text to speech using OpenAI TTS-1-HD model
def text_to_speech(text):
    # Generating text to speech using OpenAI TTS-1-HD model.
    spoken_response = client.audio.speech.create(
        model="tts-1-hd",
        voice="nova",
        response_format="opus",
        input=text
    )

    # Converting audio response to playable format and play the audio
    buffer = io.BytesIO()
    for chunk in spoken_response.iter_bytes(chunk_size = 4096):
        buffer.write(chunk)
    buffer.seek(0)

    with sf.SoundFile(buffer, 'r') as sound_file:
        data = sound_file.read(dtype = 'int16')
        sd.play(data, sound_file.samplerate)
        sd.wait()

cap = cv2.VideoCapture(0)

def live_video_description(cycle, cap=cap, window_name = 'frame'):
    if not cap.isOpened():
        return

    preview = ""
    n = 0
    i = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if keyboard.is_pressed("q"):
            break

        if n == cycle:
            n = 0
            _, buffer = cv2.imencode('.jpg', frame)
            base64_frame = base64.b64encode(buffer).decode('utf-8')
            
            # Checking if it's the first frame or not and calling the corresponding functions.
            if i == 0:
                image_description_crnt = current_frame_descriptions(base64_frame)
            else:
                image_description_crnt = continous_frame_descriptions(base64_frame_prev, base64_frame, preview)
            
            # Print and speak the generated description
            print("\n Description==========>", image_description_crnt, "\n")
            text_to_speech(text=image_description_crnt)

            # Updating the previous description and frame for the next iteration
            preview = " ".join([preview, image_description_crnt])
            base64_frame_prev = base64_frame
            i += 1
        n += 1

# Function for displaying the live feed.
def display_video(cap = cap):
    if not cap.isOpened():
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
# Main function to start the video display and description threads
def main():
    threading.Thread(target=display_video).start()
    threading.Thread(target=live_video_description, args=(5,)).start()

# Entry point of the script
if __name__ == "__main__":
    main()