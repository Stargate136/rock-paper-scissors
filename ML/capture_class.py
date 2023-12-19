from pathlib import Path
from argparse import ArgumentParser

import cv2
from mediapipe.python.solutions.hands import Hands

from .utils import get_config
from .preprocessing import extract_hand_roi


def parse_arguments():
    config_images = get_config()["images"]

    width = config_images["width"]
    height = config_images["height"]
    margin = config_images["margin"]

    parser = ArgumentParser(description="Capture images for a specific class and resize them.")

    parser.add_argument("class_folder", help="Name of the folder to save captured images.")
    parser.add_argument(
        "--desired_width",
        type=int,
        default=width,
        help=f"Desired width of the captured images. (Default: {width})."
    )
    parser.add_argument(
        "--desired_height",
        type=int,
        default=height,
        help=f"Desired height of the captured images. (Default: {height})."
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=margin,
        help=f"Margin around the region of interest. (Default: {margin}).")
    return parser.parse_args()


def capture_images(cap, hands, class_folder, desired_width, desired_height, margin):
    class_folder.mkdir(parents=True, exist_ok=True)
    counter = 0

    while True:
        ret, frame = cap.read()

        (x_start, y_start), (x_end, y_end) = extract_hand_roi(
            frame, desired_width, desired_height, margin
        )

        hand_roi = frame[y_start:y_end, x_start:x_end]

        if hand_roi.shape[0] > 0 and hand_roi.shape[1] > 0:
            resized_hand = cv2.resize(hand_roi, (desired_width, desired_height))
            key = cv2.waitKey(1)

            if key == ord('c'):
                image_path = class_folder / f'{class_folder}_{counter}.png'
                cv2.imwrite(str(image_path), resized_hand)
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

    hands = Hands(max_num_hands=1)

    class_folder = Path(args.class_folder)
    capture_images(cap, hands, class_folder, args.desired_width, args.desired_height, args.margin)


if __name__ == "__main__":
    main()
