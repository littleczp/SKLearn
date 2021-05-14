import os
import random
import sys
import time

import numpy as np

from Clustering.K_Means.HTML_CLUSTERING.main import run
from Clustering.K_Means.HTML_CLUSTERING.utils import HtmlPage

np.seterr(divide='ignore', invalid='ignore')


def get_test_data():
    for root, _, files in os.walk("./download", topdown=False):
        for f in files:
            yield os.path.join(root, f)


def load_page(file_path):
    with open(file_path, 'r') as f:
        body = f.read()
    return HtmlPage(body=body)


def test():
    test_templates = list(get_test_data())
    print("templates count:", len(test_templates))

    k = {random.choice(test_templates)}

    def add(k_clusters):
        _clt = run(load_page(t) for t in k_clusters)
        print(k_clusters)

        for i in test_templates[1:15 * len(k)]:
            _clt.add_page(load_page(i))

        for i in test_templates[:]:
            classify = _clt.classify(load_page(i))
            if classify == -1:
                k.add(i)
                return add(k)
        else:
            for i in k:
                test_file = os.path.abspath(sys.argv[0]).replace("/test.py", "")
                print("file://" + os.path.join(test_file, i[i.index("/") + 1:]))

    add(k)


if __name__ == '__main__':
    start = time.time()
    test()
    end = time.time()

    print(f"use time: {end - start}")
