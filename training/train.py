from dc.models import FlipkartQuery
from dc import app
from sklearn.svm import LinearSVC
import copy
from sklearn.feature_extraction.text import CountVectorizer
from nltk import ngrams
import string
from typing import List
from num2words import num2words
import pickle
import os

with app.app_context():
    features = [res.features for res in FlipkartQuery.query.all()]
    labels = [res.labels for res in FlipkartQuery.query.all()]
    def text_lowercase(text):
        return text.lower()
    def remove_punctuation(text):
        translator = str.maketrans('', '', string.punctuation)
        return text.translate(translator)
    # convert number into words
    def convert_number(text):
        # split string into list of words
        temp_str = text.split()
        # initialise empty list
        new_string = []
        for word in temp_str:
            # if word is a digit, convert the digit
            # to numbers and append into the new_string list
            if word.isdigit():
                temp = num2words(word)
                new_string.append(temp)
            # append the word as it is
            else:
                new_string.append(word)
        # join the words of new_string to form a string
        temp_str = ' '.join(new_string)
        return temp_str
    def preprocess_text(features: List):
        features_text = []
        for data in features:
            trim = data.strip()
            feature = trim
            feature_lower = text_lowercase(feature)
            remove_punc = remove_punctuation(feature_lower)
            convert2num = convert_number(remove_punc)
            features_text.append(convert2num)
        return features_text


    def make_grams(data, n=1):
        grammed_data = []
        for i in data:
            k = copy.deepcopy(str(i))
            for r in range(2, n + 1):
                sixgrams = ngrams(str(i).split(), r)
                for grams in sixgrams:
                    g = ""
                    for p in grams:
                        g = g + p
                    k = k + " " + g
            grammed_data.append(k)
        return grammed_data


    features_list = preprocess_text(features=features)
    text_gram = make_grams(features_list)

    # vectorize text features
    vectorizer = CountVectorizer()
    vectorizer.fit(text_gram)
    vector = vectorizer.transform(text_gram)
    feature_vector = vector.toarray()

    # train the features with labels with LinearSVC model
    svm = LinearSVC()
    svm.fit(feature_vector, labels)

    # save the model
    filepath = os.path.join(app.instance_path, 'model_files','mymodel.pkl')
    pickle.dump(svm, open(filepath, 'wb'))



