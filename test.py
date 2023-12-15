import cv2
import mediapipe as mp
import time
import math

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    print(results.multi_hand_landmarks)
    gesture = "Rien"

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            # Extraction des coordonnées des points de repère des doigts
            fingers = [4, 8, 12, 16, 20]  # Les points de repère des extrémités des doigts
            base = 0
            finger_coordinates = [(int(handLms.landmark[i].x * img.shape[1]), int(handLms.landmark[i].y * img.shape[0])) for i in fingers]
            base_coordinate = (int(handLms.landmark[base].x * img.shape[1]), int(handLms.landmark[base].y * img.shape[0]))

            # Calculer la distance euclidienne entre les extrémités des doigts
            distances = [math.dist(finger_coordinates[i], base_coordinate) for i in range(len(finger_coordinates))]
            print(distances)
            if all(distance < 200 for distance in distances):  # Condition pour la pierre basée sur avg_distance
                gesture = "Pierre"
            # Vérifier si toutes les distances sont supérieures à un seuil (tous les doigts levés)
            elif all(distance > 200 for distance in distances):  # Condition pour le papier
                gesture = "Feuille"
            elif distances[0] < 300 and distances[1] > 300 and distances[2] > 300 and distances[3] < 300 and distances[4] < 300:  # Condition pour le ciseaux
                gesture = "Ciseaux"

            # Dessiner les connexions de la main
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
    cv2.putText(img, gesture, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
