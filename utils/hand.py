from utils.core import get_hand_landmarks


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

