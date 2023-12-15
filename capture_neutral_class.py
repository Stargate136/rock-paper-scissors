import cv2
import mediapipe as mp
import os

# Initialize MediaPipe's handheld sensor
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=2,
                      min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

# Desired size of region of interest (ROI)
desired_width = 300
desired_height = 300
desired_ratio = desired_width / desired_height

# Margin around region of interest
margin = 100

# Folder for saving neutral images
neutral_folder = "neutral_images"
os.makedirs(neutral_folder, exist_ok=True)
counter = 0

# Initialize video capture
cap = cv2.VideoCapture(0)

while True:
    # Capture an image from the webcam.
    ret, frame = cap.read()
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            # Calculate minimum and maximum coordinates of hand reference points
            x_coords = [lm.x * frame.shape[1] for lm in handLms.landmark]
            y_coords = [lm.y * frame.shape[0] for lm in handLms.landmark]
            x_start, y_start = min(x_coords), min(y_coords)
            x_end, y_end = max(x_coords), max(y_coords)

            # Calculate the width and height of the bounding box
            width = int(x_end - x_start)
            height = int(y_end - y_start)

            # Calculate current aspect ratio
            current_ratio = width / height

            # Adjust width or height to match desired ratio
            if current_ratio > desired_ratio:
                new_width = int(height * desired_ratio)
                x_start += (width - new_width) // 2
                x_end = x_start + new_width
            else:
                new_height = int(width / desired_ratio)
                y_start += (height - new_height) // 2
                y_end = y_start + new_height

            # Add margin around region of interest
            x_start = max(0, int(x_start - margin))
            y_start = max(0, int(y_start - margin))
            x_end = min(frame.shape[1], int(x_end + margin))
            y_end = min(frame.shape[0], int(y_end + margin))

            # Extracting the hand area with the margin
            hand_roi = frame[y_start:y_end, x_start:x_end]

            # Check that the region of interest is not empty before resizing.
            if hand_roi.shape[0] > 0 and hand_roi.shape[1] > 0:
                # Resize hand area to desired size
                resized_hand = cv2.resize(hand_roi, (desired_width, desired_height))

                # Save image when 'c' key is pressed
                key = cv2.waitKey(1)
                if key == ord('c'):
                    image_path = os.path.join(neutral_folder, f'neutral_{counter}.png')
                    cv2.imwrite(image_path, resized_hand)
                    print(f"Recorded image : {image_path}")
                    counter += 1

                # Dessiner la boîte englobante avec la marge
                cv2.rectangle(frame, (int(x_start), int(y_start)), (int(x_end), int(y_end)), (0, 255, 0), 2)

    # Afficher l'image en temps réel
    cv2.imshow('Capture Neutral Class', frame)

    # Quitter la boucle si la touche 'q' est enfoncée.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer la capture vidéo et fermer les fenêtres
cap.release()
cv2.destroyAllWindows()
