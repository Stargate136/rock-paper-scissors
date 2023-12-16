import json

import cv2
import mediapipe as mp

from utils import calculate_bounding_box, adjust_aspect_ratio, detect_finger_positions, distance_to_base


hands = mp.solutions.hands.Hands(max_num_hands=1)


def extract_hand_roi(frame, desired_width, desired_height, margin):
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    hand_landmarks = None
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
    if hand_landmarks is not None:
        bounding_box = calculate_bounding_box(hand_landmarks, frame.shape, margin)

        x_start, y_start, x_end, y_end, width, height = bounding_box

        x_start, y_start, x_end, y_end = adjust_aspect_ratio(
            x_start, y_start, x_end, y_end, frame.shape, desired_width / desired_height
        )
        return (x_start, y_start), (x_end, y_end)


def get_hand_roi(frame, start_position, end_position):
    x_start, y_start = start_position
    x_end, y_end = end_position
    return frame[y_start:y_end, x_start:x_end]


def get_features(image):
    finger_coordinates = detect_finger_positions(image)
    return [distance_to_base(finger_coordinates, i) for i in range(5)]


def pipeline(image, return_hand_roi_position=False):
    with open("config.json", "r") as f:
        config_images = json.load(f)["images"]

    width = config_images["width"]
    height = config_images["height"]
    margin = config_images["margin"]

    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    hand_roi_position = extract_hand_roi(
        img_rgb, width, height, margin
    )
    if hand_roi_position is not None:
        start_pos, end_pos = hand_roi_position
        hand_roi = get_hand_roi(img_rgb, start_pos, end_pos)

        features = get_features(hand_roi)

        if return_hand_roi_position:
            return features, (start_pos, end_pos)
        return features
