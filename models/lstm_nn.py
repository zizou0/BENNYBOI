import sys
import os
import tensorflow as tf
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join('..', '/Users/benedictzuzi/Documents/nlp_sentiment_analysis/src')))
from preprocess import preprocess


from keras.preprocessing.text import Tokenizer
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from keras.callbacks import ModelCheckpoint


filename = '/Users/benedictzuzi/Documents/nlp_sentiment_analysis/data/imdb_dataset.csv'

df = preprocess(filename)  
sentiments_encoded = df['sentiment'].map({'positive': 1, 'negative': 0})

def padding_sequences(encoded_reviews, sequence_length):
    features = np.zeros((len(encoded_reviews), sequence_length), dtype=int)
    for i, review in enumerate(encoded_reviews):
        if len(review) != 0:
            features[i, -len(review):] = np.array(review)[:sequence_length]
    return features


def text_to_padded_sequences(texts):
    # Create the tokenizer object and fit it to the texts
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(texts)

    # Convert texts to sequences of integers
    sequences = tokenizer.texts_to_sequences(texts)

    # Get the vocabulary size for future use 
    vocab_size = len(tokenizer.word_index) + 1  # Adding 1 because of reserved 0 index

    # Pad sequences to the same length
    max_length = max(len(seq) for seq in sequences)  # Use max length if not provided
    padded_sequences = padding_sequences(sequences, max_length)

    return padded_sequences, vocab_size, tokenizer

# main preprocessing function
def preprocess_for_lstm(df):
    
    # Convert the cleaned reviews to padded sequences
    padded_sequences, vocab_size, tokenizer = text_to_padded_sequences(df['cleaned_review'])
    
    
    return padded_sequences, vocab_size, tokenizer




padded_sequences, vocab_size, tokenizer = preprocess_for_lstm(df)

X = df  
y = df['sentiment'].map({'positive': 1, 'negative': 0})  # This maps text labels to binary

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train_vect, vocab_size_train, tokenizer_train = preprocess_for_lstm(X_train)
X_test_vect,  vocab_size_test, tokenizer_test = text_to_padded_sequences(X_test)

embedding_dim = 32  # Size of the word embeddings

model = Sequential()
model.add(Embedding(input_dim=vocab_size, output_dim=embedding_dim))
model.add(LSTM(units=50, return_sequences=False))  # units are the dimensionality of the output space
model.add(Dropout(0.5))  # Dropout for regularization
model.add(Dense(1, activation='sigmoid'))  # Output layer with sigmoid activation for binary classification


model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

print(model.summary())



checkpoint = ModelCheckpoint(
    '/Users/benedictzuzi/Documents/nlp_sentiment_analysismodels/lstm_nn.py',
    monitor='accuracy',
    save_best_only=True,
    verbose=1
)

history = model.fit(padded_sequences, sentiments_encoded, batch_size=128, epochs=5, callbacks=[checkpoint])



y_pred = model.predict_step(X_test_vect, batch_size = 128)

true = 0
for i, y in enumerate(y_test):
    if y == y_pred[i]:
        true += 1

print('Accuracy: {}'.format(true/len(y_pred)*100))






if __name__ == "__main__":
    max_sequence_length = 100  # This is an arbitrary number; you might need to optimize it
    processed_data, vocab_size, tokenizer = preprocess_for_lstm(df)
    print(processed_data.shape)  # Should show (num_samples, max_sequence_length)



