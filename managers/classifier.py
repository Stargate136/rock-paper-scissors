import numpy as np

from ML import train_model, preprocess_image


class ClassifierManager:
    def __init__(self):
        self._model = train_model()

    def predict(self, image):
        X = preprocess_image(image)
        if not np.isnan(X).any():
            prediction = self._model.predict([X])[0]
            if prediction != "neutral":
                return prediction
