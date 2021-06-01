# spam
> Model: Naive Bayes、SVC<br>
> Theory: TF-IDF、Laplace smoothing(0.2)<br>
> Approaches: Bayes theorem

# Directory
```
data/                    # main data_set(from https://www.kaggle.com/benvozza/spam-classification)
test/                    # test Spam
utils/
    __init__.py          # build dom structure
    pre_processor.py     # handle email header and body

./
    __init__.py
    main.py              # build bayes model
```

step|purpose|how
---|---|---
1|Text analytics|Extracting words stem other than stop words
2|TF-IDF|calculate term frequency–inverse document frequency
3|Generate bayes model|Split train set and test set, then fit it to model

#### feature vectors
```
1. extract html text: regex pattern + bs4.get_text()

2. words stem(only english) and remove stop words  # Not required
    nltk.stem.SnowballStemmer("english")

    >>> testing          # test
    >>> tested           # test
    >>> test             # test
    >>> 测试              # 测试
    >>> テスト            # テスト
    >>> eb_well_testing  # eb_well_test

3. calculate tf-idf(feature vectors): sklearn.feature_extraction.text.TfidfVectorizer

4. fit feature vectors and labels to models(bayes, svc)
```

### How to use
##### train from csv
1. According to the origin format`(label, text,,,)`, fill `/data/spam.csv`
2. Run `bayes.py`

##### train from file directory
1. Place the templates in the `test/download` folder, distinguish labels `test/download/Invalid` & `others`
2. Run `test/test.py`
```
test/
    download/
        Invalid/
            ...    # invalid emails
        xxx/
            ...    # legal emails
```

### Reference
1. [naive bayes](https://scikit-learn.org/stable/modules/naive_bayes.html#multinomial-naive-bayes)
2. [kaggle spam classification](https://www.kaggle.com/benvozza/spam-classification)

### Thanks for
@gq.wu
