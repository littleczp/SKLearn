import os
import tempfile

import joblib
import pandas
from tqdm import tqdm

from Classification.Naive_Bayes.Spam.bayes import BayesModel
from Classification.Naive_Bayes.Spam.utils.pre_processor import processor


def model_from_cache():
    model_path = os.path.join(os.getcwd(), "../data/filter.model")
    if os.path.exists(model_path):
        return joblib.load(model_path)


def get_invalid_set():
    for root, dirs, files in os.walk(os.path.join(os.getcwd(), "download/Invalid")):
        for file in files:
            if file.endswith(".html") or file.endswith(".gz"):
                yield f"{root}/{file}"


def get_legal_set():
    for root, dirs, files in os.walk(os.path.join(os.getcwd(), "download/")):
        for file in files:
            if not root.endswith("Invalid") and (file.endswith(".html") or file.endswith(".gz")):
                yield f"{root}/{file}"


def turn_feature_vectors(file_path: str, dataframe: pandas.DataFrame, label: str):
    with open(file_path) as file:
        email_body = file.read()
    try:
        email_body = processor.get_email_body(email_body)
        dataframe.loc[len(dataframe)] = [label, email_body]
    except Exception as err:
        print(err)


def training_set_from_cache():
    invalid_path = os.path.join(os.getcwd(), "../data/invalid.csv")
    if not os.path.exists(invalid_path):
        invalid_dataframe = pandas.DataFrame(columns=["label", "text"])
        invalid_set = list(get_invalid_set())
        list(map(lambda x: turn_feature_vectors(x, invalid_dataframe, "invalid"), tqdm(invalid_set, desc="invalid")))
        with open(invalid_path, "w", encoding='utf-8_sig', errors='ignore', newline="") as path:
            invalid_dataframe.to_csv(path_or_buf=path, index=False)
    else:
        invalid_dataframe = pandas.read_csv(invalid_path)

    legal_path = os.path.join(os.getcwd(), "../data/legal.csv")
    if not os.path.exists(legal_path):
        legal_dataframe = pandas.DataFrame(columns=["label", "text"])
        legal_set = list(get_legal_set())
        list(map(lambda x: turn_feature_vectors(x, legal_dataframe, "legal"), tqdm(legal_set, desc="legal")))
        with open(legal_path, "w", encoding='utf-8_sig', errors='ignore', newline="") as path:
            legal_dataframe.to_csv(path_or_buf=path, index=False)
    else:
        legal_dataframe = pandas.read_csv(legal_path)

    dataframe = pandas.concat([invalid_dataframe, legal_dataframe], sort=False)
    return dataframe.reset_index()


if __name__ == '__main__':
    # 判断是否存在已训练好的模型，`data/filter.model`, 如果需要重新生成, 请删除这个文件
    # model will load from `data/filter.model`, if need to regenerate model, please delete the file
    model = model_from_cache()
    if not model:
        # 生成模型将使用 `data/invalid.csv` 以及 `data/legal.csv` 作为训练集，如果需要重新生成训练集，请删除这些文件
        # generate model will use `data/invalid.csv` and `data/legal.csv` as training set
        # if need to regenerate the training set, please delete the files
        data = training_set_from_cache()

        with tempfile.NamedTemporaryFile() as temp:
            data.to_csv(temp.name)
            model = BayesModel().train_from_csv(temp.name)
            joblib.dump(model, os.path.join(os.getcwd(), "../data/filter.model"))

    predict_text = "Test text"
    predict = model.predict_text(predict_text)
    print(predict)
