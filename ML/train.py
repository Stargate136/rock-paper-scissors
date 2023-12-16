import json

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC


def train_model():
    with open("config.json", "r") as f:
        features_url = json.load(f)["features"]["url"]
    df = pd.read_csv(features_url)

    X = df.drop(["target"], axis=1).values
    y = df["target"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = SVC().fit(X_train, y_train)

    print("train score: ", clf.score(X_train, y_train))
    print("test score: ", clf.score(X_test, y_test))

    return clf
