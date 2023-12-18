import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from .utils import get_config


def train_model():
    dataset_url = get_config()["datasets"][-1]["url"]
    df = pd.read_csv(dataset_url)

    X = df.drop(["target"], axis=1).values
    y = df["target"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = SVC().fit(X_train, y_train)

    print("train score: ", clf.score(X_train, y_train))
    print("test score: ", clf.score(X_test, y_test))

    return clf
