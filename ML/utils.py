import cv2
import mediapipe as mp
import numpy as np


hands = mp.solutions.hands.Hands(max_num_hands=1)


def get_hand_landmarks(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        return results.multi_hand_landmarks[0]


def detect_finger_positions(image):

    hand_landmarks = get_hand_landmarks(image)
    if hand_landmarks is None:
        return []

    finger_coordinates = []
    for landmark in hand_landmarks.landmark:
        finger_coordinates.append((landmark.x, landmark.y, landmark.z))

    return finger_coordinates


def compute_distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2) ** 0.5


def distance_to_base(finger_coordinates, finger_idx):
    # Extraire les coordonnées des points de repère des doigts
    finger_tip_idxs = [4, 8, 12, 16, 20]

    # Récupérer les coordonnées du bout du doigt
    finger_tip_idx = finger_tip_idxs[finger_idx]
    try:
        finger_tip_coordinates = finger_coordinates[finger_tip_idx]

        base_coordinates = finger_coordinates[0]

        # Calculer la distance entre le doigt et la main
        distance = compute_distance(finger_tip_coordinates, base_coordinates)

        return distance
    except IndexError:
        return np.nan


def calculate_bounding_box(hand_landmarks, frame_shape, margin):

    x_coords = [lm.x * frame_shape[1] for lm in hand_landmarks.landmark]
    y_coords = [lm.y * frame_shape[0] for lm in hand_landmarks.landmark]
    x_start, y_start = min(x_coords), min(y_coords)
    x_end, y_end = max(x_coords), max(y_coords)

    width = int(x_end - x_start)
    height = int(y_end - y_start)

    return (
        max(0, int(x_start - margin)),
        max(0, int(y_start - margin)),
        min(frame_shape[1], int(x_end + margin)),
        min(frame_shape[0], int(y_end + margin)),
        width,
        height
    )


def adjust_aspect_ratio(x_start, y_start, x_end, y_end, frame_shape, desired_ratio):
    current_ratio = (x_end - x_start) / (y_end - y_start)

    if current_ratio > desired_ratio:
        new_width = int((y_end - y_start) * desired_ratio)
        x_start += (x_end - x_start - new_width) // 2
        x_end = x_start + new_width
    else:
        new_height = int((x_end - x_start) / desired_ratio)
        y_start += (y_end - y_start - new_height) // 2
        y_end = y_start + new_height

    return (
        max(0, int(x_start)),
        max(0, int(y_start)),
        min(frame_shape[1], int(x_end)),
        min(frame_shape[0], int(y_end))
    )
