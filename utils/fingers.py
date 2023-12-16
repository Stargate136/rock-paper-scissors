import numpy as np

from .core import get_hand_landmarks


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
