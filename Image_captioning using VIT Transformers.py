import torch
import cv2
import numpy as np
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import tempfile
import warnings,logging
warnings.simplefilter('ignore')
logging.disable(logging.WARNING)



# Transformer and Pretrained Model
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, GPT2TokenizerFast
# Managing loading processsing
from tqdm import tqdm

# Assign available GPU
device = "cuda" if torch.cuda.is_available() else "cpu"

# ViT Encoder - Decoder Model
model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning").to(device)

# Corresponding ViT Tokenizer
tokenizer = GPT2TokenizerFast.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

# Image processor
image_processor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

# Image inference
def get_caption(model, image_processor, tokenizer, image):

    # Preprocessing the Image
    img = image_processor(image, return_tensors = "pt").to(device)

    # Generating captions
    output = model.generate(**img)

    # decode the output
    caption = tokenizer.batch_decode(output, skip_special_tokens = True)[0]

    return caption



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



# Function to detect scene change
def is_scene_change(current_frame, previous_frame, threshold = 1000):
    # Calculate difference
    difference = cv2.absdiff(current_frame, previous_frame)
    non_zero_count = np.count_nonzero(difference)
    return non_zero_count > threshold

# Initialize webcam
cap = cv2.VideoCapture(0)
ret, previous_frame = cap.read()

while True:
    ret, current_frame = cap.read()
    if not ret:
        break

    # Check for scene change
    if is_scene_change(current_frame, previous_frame):
        # Process the frame for captioning
        caption = get_caption(model, image_processor, tokenizer, current_frame)
        print(caption)
        T_T_speech(caption)
        previous_frame = current_frame.copy()

    # Display the frame
    cv2.imshow('Webcam Feed', current_frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
