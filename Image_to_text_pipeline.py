import warnings
import logging
import cv2
import numpy as np
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import tempfile
from PIL import Image
import os

# Set the environment variable
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

warnings.simplefilter('ignore')
logging.disable(logging.WARNING)

from transformers import pipeline
caption = pipeline('image-to-text')

def T_T_speech(text, Language='en'):
    try:
        # Generate speech
        myobj = gTTS(text=text, lang=Language, slow=False)

        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as fp:
            myobj.write_to_fp(fp)
            fp.seek(0)

            # Read the audio file and play it
            with sf.SoundFile(fp.name, 'r') as sound_file:
                data = sound_file.read(dtype='int16')
                sd.play(data, sound_file.samplerate)
                sd.wait()

    except Exception as e:
        print(f"An error occurred: {e}")

def is_scene_change(current_frame, previous_frame, threshold=1000):
    # Calculate difference
    difference = cv2.absdiff(current_frame, previous_frame)
    non_zero_count = np.count_nonzero(difference)
    return non_zero_count > threshold

cap = cv2.VideoCapture(0)
ret, previous_frame = cap.read()

while True:
    ret, current_frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break

    # Check for scene change
    if is_scene_change(current_frame, previous_frame):
        # Convert OpenCV frame (BGR) to PIL Image (RGB)
        frame_rgb = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)

        # Process the frame for captioning
        try:
            captions = caption(pil_image)
            captions_text = str(captions)  # Convert captions to string if necessary
            print(captions_text['generated_text'])
            T_T_speech(captions_text['generated_text'])
        except Exception as e:
            print(f"Error in captioning: {e}")

        previous_frame = current_frame.copy()

    cv2.imshow('Webcam Feed', current_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
