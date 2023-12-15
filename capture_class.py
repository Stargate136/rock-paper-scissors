import cv2
import mediapipe as mp
import os
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="Capture images for a specific class.")
    parser.add_argument("class_folder", help="Name of the folder to save captured images.")
    parser.add_argument("--desired_width", type=int, default=300, help="Desired width of the captured images.")
    parser.add_argument("--desired_height", type=int, default=300, help="Desired height of the captured images.")
    parser.add_argument("--margin", type=int, default=100, help="Margin around the region of interest.")
    return parser.parse_args()


def initialize_hand_tracking():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                           min_detection_confidence=0.5, min_tracking_confidence=0.5)
    return hands


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


def adjust_aspect_ratio(x_start, y_start, x_end, y_end, frame_shape, desired_width, desired_height, desired_ratio):
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


def capture_images(cap, hands, class_folder, desired_width, desired_height, margin):
    os.makedirs(class_folder, exist_ok=True)
    counter = 0

    while True:
        ret, frame = cap.read()
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                x_start, y_start, x_end, y_end, width, height = calculate_bounding_box(
                    hand_landmarks, frame.shape, margin
                )

                x_start, y_start, x_end, y_end = adjust_aspect_ratio(
                    x_start, y_start, x_end, y_end, frame.shape, desired_width, desired_height, desired_width / desired_height
                )

                hand_roi = frame[y_start:y_end, x_start:x_end]

                if hand_roi.shape[0] > 0 and hand_roi.shape[1] > 0:
                    resized_hand = cv2.resize(hand_roi, (desired_width, desired_height))
                    key = cv2.waitKey(1)

                    if key == ord('c'):
                        image_path = os.path.join(class_folder, f'{class_folder}_{counter}.png')
                        cv2.imwrite(image_path, resized_hand)
                        print(f"Recorded image : {image_path}")
                        counter += 1

                cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)

        cv2.imshow('Capture Images', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print(f"Captured {counter} images.")
    cap.release()
    cv2.destroyAllWindows()


def main():
    args = parse_arguments()

    print(f"Capturing images for {args.class_folder}...")
    print(f"Desired width : {args.desired_width}")
    print(f"Desired height : {args.desired_height}")
    print(f"Margin : {args.margin}")

    print("Press 'c' to capture an image")
    print("Press 'q' to quit")

    cap = cv2.VideoCapture(0)
    hands = initialize_hand_tracking()

    capture_images(cap, hands, args.class_folder, args.desired_width, args.desired_height, args.margin)


if __name__ == "__main__":
    main()
