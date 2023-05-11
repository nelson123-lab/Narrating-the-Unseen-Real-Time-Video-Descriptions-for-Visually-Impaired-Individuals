import numpy as np
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, LSTM, Embedding
from tensorflow.keras.utils import to_categorical

# Load and preprocess the image
def preprocess_image(image_path):
    img = load_img(image_path, target_size=(224, 224))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = VGG16.preprocess_input(img)
    return img

# Load the pre-trained VGG16 model
vgg16 = VGG16(weights='imagenet', include_top=True)
vgg16 = Model(inputs=vgg16.input, outputs=vgg16.get_layer('fc2').output)

# Load and preprocess the captions
def preprocess_captions(captions):
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(captions)
    sequences = tokenizer.texts_to_sequences(captions)
    word_index = tokenizer.word_index
    vocab_size = len(word_index) + 1
    max_sequence_len = max(len(seq) for seq in sequences)

    X, y = [], []
    for seq in sequences:
        for i in range(1, len(seq)):
            in_seq, out_seq = seq[:i], seq[i]
            in_seq = pad_sequences([in_seq], maxlen=max_sequence_len)[0]
            out_seq = to_categorical([out_seq], num_classes=vocab_size)[0]
            X.append(in_seq)
            y.append(out_seq)
    
    return np.array(X), np.array(y), vocab_size, max_sequence_len

# Define the image captioning model
def create_model(vocab_size, max_sequence_len):
    inputs1 = Input(shape=(4096,))
    fe1 = Dropout(0.5)(inputs1)
    fe2 = Dense(256, activation='relu')(fe1)
    inputs2 = Input(shape=(max_sequence_len,))
    se1 = Embedding(vocab_size, 256, mask_zero=True)(inputs2)
    se2 = Dropout(0.5)(se1)
    se3 = LSTM(256)(se2)
    decoder1 = add([fe2, se3])
    decoder2 = Dense(256, activation='relu')(decoder1)
    outputs = Dense(vocab_size, activation='softmax')(decoder2)
    model = Model(inputs=[inputs1, inputs2], outputs=outputs)
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model

# Generate captions for a given image
def generate_caption(image_path, model, tokenizer, max_sequence_len):
    in_text = 'startseq'
    for _ in range(max_sequence_len):
        sequence = tokenizer.texts_to_sequences([in_text])[0]
        sequence = pad_sequences([sequence], maxlen=max_sequence_len)
        yhat = model.predict([image, sequence], verbose=0)
        yhat = np.argmax(yhat)
        word = word_for_id(yhat, tokenizer)
        if word is None:
            break
        in_text += ' ' + word
        if word == 'endseq':
            break
    return in_text

# Example usage
image_path = 'example_image.jpg'
captions = ['A cat is sitting on a mat.', 'A dog is running in a field.']

# Preprocess the image and captions
image = preprocess_image(image_path)
