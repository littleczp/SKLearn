import os
import time

import pandas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

from Classification.Naive_Bayes.Spam.utils.pre_processor import processor


class BayesModel:
    def __init__(self):
        self.model = None
        self.vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w\w{1,30}\b")

    def predict_text(self, text):
        text = pandas.Series(text)
        tf_idf = self.vectorizer.transform(text)
        return self.model.predict(tf_idf)

    def train_from_csv(self, path):
        print("*" * 15, "generate model", "*" * 15)
        file = os.path.join(os.getcwd(), path)
        data = pandas.read_csv(file)

        X_train, X_test, y_train, y_test = self.__pre_process(data)

        train_time = time.time()
        print("train start")
        self.model = self.__train(X_train, y_train)
        print("train use: ", time.time() - train_time)

        print("Accuracy:", self.model.score(X_test, y_test))

        y_predict = self.model.predict(X_test)
        print("DataFrame:", classification_report(y_test, y_predict))
        return self

    def __pre_process(self, data):
        t1 = time.time()
        print("words_stem start")
        # text = data["text"].apply(processor.get_words_stem)
        text = data["text"]
        print("words_stem use: ", time.time() - t1)

        X_train, X_test, y_train, y_test = train_test_split(text, data["label"], test_size=0.25, random_state=33)

        tf_idf_time = time.time()
        print("tf_idf start")
        X_train = self.vectorizer.fit_transform(X_train)
        X_test = self.vectorizer.transform(X_test)
        print("tf_idf use: ", time.time() - tf_idf_time)

        return X_train, X_test, y_train, y_test

    def __train(self, x_train, y_train):
        # model = MultinomialNB(fit_prior=False, class_prior=[0.95, 0.05])
        """
        Accuracy: 0.9424397794331044
        DataFrame:    precision    recall  f1-score   support

            invalid       0.90      0.99      0.94      5043
            legal         0.99      0.89      0.94      5294

            accuracy                          0.94     10337
            macro avg     0.95      0.94      0.94     10337
            weighted avg  0.95      0.94      0.94     10337
        """

        model = MultinomialNB(alpha=0.1)
        """
        Accuracy: 0.9666247460578504
        DataFrame:    precision    recall  f1-score   support

            invalid       0.97      0.96      0.97      5043
            legal         0.96      0.97      0.97      5294

            accuracy                          0.97     10337
            macro avg     0.97      0.97      0.97     10337
            weighted avg  0.97      0.97      0.97     10337
        """

        # model = SVC(kernel='linear', gamma=1.0, verbose=5)
        """
        DataFrame:      precision    recall  f1-score   support

            invalid         0.99      0.99      0.99      5043
            legal           0.99      0.99      0.99      5294

            accuracy                            0.99     10337
            macro avg       0.99      0.99      0.99     10337
            weighted avg    0.99      0.99      0.99     10337
        """

        # model = SVC(kernel='sigmoid', gamma=1.0, verbose=5)
        """
        Accuracy: 0.9891651349521138
        DataFrame:      precision    recall  f1-score   support

            invalid        0.99       0.99      0.99      5043
            legal          0.99       0.99      0.99      5294

            accuracy                            0.99     10337
            macro avg      0.99       0.99      0.99     10337
            weighted avg   0.99       0.99      0.99     10337
        """
        model.fit(x_train, y_train)
        return model


if __name__ == '__main__':
    bayes_model = BayesModel()
    bayes_model.train_from_csv("data/spam.csv")
