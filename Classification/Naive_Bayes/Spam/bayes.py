import os

import pandas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

from Classification.Naive_Bayes.Spam.utils.pre_processor import processor


class BayesModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w\w{1,30}\b")

    def predict(self):
        ...

    def train_from_csv(self, path="data/spam.csv"):
        file = os.path.join(os.getcwd(), path)
        data = pandas.read_csv(file)
        text = data["text"].apply(processor.get_words_stem)  # Accuracy: 0.9318018664752333
        # text = data["text"]  # Accuracy: 0.9260588657573582

        features = self.__td_idf(text)
        X_train, X_test, y_train, y_test = train_test_split(features, data['label'], test_size=0.25, random_state=33)
        model = self.__train(X_train, y_train)

        print("Accuracy:", model.score(X_test, y_test))

    def __td_idf(self, text):
        return self.vectorizer.fit_transform(text)

    def __train(self, x_train, y_train):
        model = MultinomialNB(fit_prior=False, class_prior=[0.95, 0.05])  # 0.93
        # model = MultinomialNB(alpha=0.2)  # 0.9827
        # model = SVC(kernel='sigmoid', gamma=1.0)  # 0.9806
        model.fit(x_train, y_train)
        return model


if __name__ == '__main__':
    model = BayesModel()
    model.train_from_csv()
