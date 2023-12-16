import json

import cv2

from utils.fingers import detect_finger_positions, distance_to_base
from utils.hand import get_hand_roi, extract_hand_roi


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
