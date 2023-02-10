# Install dependencies
import flask
import pickle
import pandas as pd
import numpy as np
import nltk
import string
import re
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('pros_cons')
nltk.download('reuters')

# Load pre-trained model
with open(f'model/twitter_predictions.pkl', 'rb') as f:
    model = pickle.load(f)

with open(f'model/vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)


# Remove URLs
def remove_url(text):
    return re.sub(r"http\S+", "", text)

# Removing Punctuations
def remove_punct(text):
    new_text = []
    for t in text:
        if t not in string.punctuation:                      
            new_text.append(t)
    return ''.join(new_text)

#Tokenizer
from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')

#Removing Stop words
from nltk.corpus import stopwords

def remove_sw(text):
    new_text = []
    for t in text:
        if t not in stopwords.words('english'):
            new_text.append(t)
    return new_text                                                       

#Lemmatizaion
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

def word_lemmatizer(text):
    new_text = []
    for t in text:
        lem_text = lemmatizer.lemmatize(t)
        new_text.append(lem_text)
    return new_text


app = flask.Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET','POST'])
def main():
    if flask.request.method == 'GET':
        return flask.render_template('main.html')

    if flask.request.method == 'POST':
        tweet_temp = flask.request.form['tweet']
        app.logger.info(tweet_temp)
        tweet = [tweet_temp]
        df = pd.DataFrame(tweet,columns=['tweet'])
        df['tweet'] = df['tweet'].apply(lambda t: remove_url(t))
        df['tweet'] = df['tweet'].apply(lambda t: remove_punct(t))
        df['tweet'] = df['tweet'].apply(lambda t: tokenizer.tokenize(t.lower()))
        df['tweet'] = df['tweet'].apply(lambda t: remove_sw(t))
        df['tweet'] = df['tweet'].apply(lambda t: word_lemmatizer(t))

        final_text = df['tweet']
        final_text.iloc[0] = ' '.join(final_text.iloc[0])
        X = vectorizer.transform(final_text)
        prediction = model.predict_proba(X)
        positive = round(prediction[0][0] * 100)
        negative = round(prediction[0][1] * 100)
        
        return flask.render_template('main.html', original_input={'Review':tweet_temp}, rating1=positive, rating2=negative)

if __name__ == '__main__':
    app.run()