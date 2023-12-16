import numpy as np

import cv2

import preprocessing
from train import train_model


def main():
    clf = train_model()

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()

        features = preprocessing.pipeline(frame, return_hand_roi_position=True)
        if features is not None:
            X, (start_pos, end_pos) = features
            if not np.isnan(X).any():
                pred = clf.predict([X])

                cv2.putText(frame, str(pred), (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

            cv2.rectangle(frame, start_pos, end_pos, (0, 255, 0), 2)

        cv2.imshow('Capture Images', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
