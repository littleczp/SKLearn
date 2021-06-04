import os
import random
import sys
import time
from collections import defaultdict
from pprint import pprint

import numpy as np
from tqdm import tqdm

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
    cur, err = list(), set()
    cache = defaultdict(lambda: 0)
    queue = [random.choice(test_templates)]
    while queue:
        cache = defaultdict(lambda: 0)
        cur.append(queue.pop(0))

        _clt = run(load_page(i) for i in cur)

        test_range = len(test_templates) // 3 * len(cur)
        for i in test_templates[: test_range]:
            _clt.add_page(load_page(i))

        for i in tqdm(test_templates):
            try:
                classify = _clt.classify(load_page(i))
            except Exception as e:
                print(e)
                err.add(os.path.join(os.path.abspath(sys.argv[0]).replace("/test.py", ""), i[i.index("/") + 1:]))
                continue

            if classify == -1:
                queue.append(i)
                break

            cache[classify] += 1
        else:
            break

    res = dict()
    for i, n in enumerate(cur):
        test_file = os.path.join(os.path.abspath(sys.argv[0]).replace("/test.py", ""), n[n.index("/") + 1:])
        res["file://" + test_file] = cache[i]

    print("***" * 15, "\n")
    for i in err:
        print("error file_path file://" + i)

    pprint({(v, "{:.2%}".format(v / len(test_templates))): k for k, v in sorted(res.items(), key=lambda x: -x[1])}, sort_dicts=False)


if __name__ == '__main__':
    start = time.time()
    test()
    end = time.time()

    print(f"use time: {end - start}")
