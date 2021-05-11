import os
import warnings

import numpy as np

from Clustering.K_Means.HTML_CLUSTERING.feature import tag_freq as vectorizer
from Clustering.K_Means.HTML_CLUSTERING.utils import build_dom
from Clustering.K_Means.HTML_CLUSTERING.utils.html import HtmlPage
from Clustering.K_Means.HTML_CLUSTERING.kmeans import KMeans

warnings.simplefilter(action='ignore', category=FutureWarning)


def run(templates):
    # turn template to feature vector
    pages = list(map(build_dom, templates))
    k_clusters = len(pages)
    centers = list(map(vectorizer, pages))
    X = np.zeros((len(centers), vectorizer.dimension))
    for i, c in enumerate(centers):
        X[i, :len(c)] = c
    return KMeans(k_clusters=k_clusters, centers=X,
                  min_cluster_points=5, max_std_dev=3,  # find_outliers parameter
                  vectorizer=vectorizer)


if __name__ == '__main__':
    JOBS = [
        'Jobs - 1 - Stack Overflow.html',
        'Jobs - 2 - Stack Overflow.html',
        'Jobs - 3- Stack Overflow.html',
        'Jobs - 4 - Stack Overflow.html',
        'Jobs - 5 - Stack Overflow.html',
        'Jobs - 6 - Stack Overflow.html',
        'Jobs - 7 - Stack Overflow.html',
        'Jobs - 8 - Stack Overflow.html',
        'Jobs - 9 - Stack Overflow.html',
        'Jobs - 10 - Stack Overflow.html',
        'Jobs - 11 - Stack Overflow.html',
        'Jobs - 12 - Stack Overflow.html',
        'Jobs - 13 - Stack Overflow.html',
        'Jobs - 14 - Stack Overflow.html',
        'Jobs - 15 - Stack Overflow.html',
    ]

    QUESTION_LIST = [
        'Newest Questions - Page 1 - Stack Overflow.html',
        'Newest Questions - Page 2 - Stack Overflow.html',
        'Newest Questions - Page 3 - Stack Overflow.html',
        'Newest Questions - Page 4 - Stack Overflow.html',
        'Newest Questions - Page 5 - Stack Overflow.html',
        'Newest Questions - Page 6 - Stack Overflow.html',
        'Newest Questions - Page 7 - Stack Overflow.html',
        'Newest Questions - Page 8 - Stack Overflow.html',
        'Newest Questions - Page 9 - Stack Overflow.html',
        'Newest Questions - Page 10 - Stack Overflow.html',
        'Newest Questions - Page 11 - Stack Overflow.html',
        'Newest Questions - Page 12 - Stack Overflow.html',
        'Newest Questions - Page 13 - Stack Overflow.html',
        'Newest Questions - Page 14 - Stack Overflow.html',
        'Newest Questions - Page 15 - Stack Overflow.html',
    ]

    QUESTION_DETAIL = [
        'Question - 1 - Stack Overflow.html',
        'Question - 2 - Stack Overflow.html',
        'Question - 3 - Stack Overflow.html',
        'Question - 4 - Stack Overflow.html',
        'Question - 5 - Stack Overflow.html',
        'Question - 6 - Stack Overflow.html',
        'Question - 7 - Stack Overflow.html',
        'Question - 8 - Stack Overflow.html',
        'Question - 9 - Stack Overflow.html',
        'Question - 10 - Stack Overflow.html',
        'Question - 11 - Stack Overflow.html',
        'Question - 12 - Stack Overflow.html',
        'Question - 13 - Stack Overflow.html',
        'Question - 14 - Stack Overflow.html',
        'Question - 15 - Stack Overflow.html',
    ]

    TAGS = [
        'Tags - 1 - Stack Overflow.html',
        'Tags - 2 - Stack Overflow.html',
        'Tags - 3 - Stack Overflow.html',
        'Tags - 4 - Stack Overflow.html',
        'Tags - 5 - Stack Overflow.html',
        'Tags - 6 - Stack Overflow.html',
        'Tags - 7 - Stack Overflow.html',
        'Tags - 8 - Stack Overflow.html',
        'Tags - 9 - Stack Overflow.html',
        'Tags - 10 - Stack Overflow.html',
        'Tags - 11 - Stack Overflow.html',
        'Tags - 12 - Stack Overflow.html',
        'Tags - 13 - Stack Overflow.html',
        'Tags - 14 - Stack Overflow.html',
        'Tags - 15 - Stack Overflow.html',
    ]

    USERS = [
        'Users - 1 - Stack Overflow.html',
        'Users - 2 - Stack Overflow.html',
        'Users - 3 - Stack Overflow.html',
        'Users - 4 - Stack Overflow.html',
        'Users - 5 - Stack Overflow.html',
        'Users - 6 - Stack Overflow.html',
        'Users - 8 - Stack Overflow.html',
        'Users - 9 - Stack Overflow.html',
        'Users - 10 - Stack Overflow.html',
        'Users - 11 - Stack Overflow.html',
        'Users - 12 - Stack Overflow.html',
        'Users - 13 - Stack Overflow.html',
        'Users - 14 - Stack Overflow.html',
        'Users - 15 - Stack Overflow.html',
    ]

    ALL = [
        JOBS,
        QUESTION_LIST,
        QUESTION_DETAIL,
        TAGS,
        USERS
    ]

    def load_page(name, path='data'):
        with open(os.path.join(".", path, name), 'r') as f:
            body = f.read()
        return HtmlPage(body=body)


    # step1: fit k
    clt = run(load_page(group[0]) for group in ALL)
    # step2: calculate centroid
    for group in ALL:
        for name in group[1:11]:
            clt.add_page(load_page(name))

    # step3: classify clusters
    for i, group in enumerate(ALL):
        for name in group:
            classify = clt.classify(load_page(name))
            print(i, classify, classify == i)
