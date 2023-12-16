import cv2
import mediapipe as mp

hands = mp.solutions.hands.Hands(max_num_hands=1)


def get_hand_landmarks(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        return results.multi_hand_landmarks[0]

