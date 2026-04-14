from arcade_app.constants import BASE_HEIGHT, BASE_WIDTH


def scale_x(actual_width: int, value: int | float) -> int:
    return int((actual_width / BASE_WIDTH) * value)


def scale_y(actual_height: int, value: int | float) -> int:
    return int((actual_height / BASE_HEIGHT) * value)