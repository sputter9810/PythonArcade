from pygame import Rect

from arcade_app.constants import CONTENT_PADDING, FOOTER_HEIGHT, HEADER_HEIGHT


def header_rect(width: int) -> Rect:
    return Rect(0, 0, width, HEADER_HEIGHT)


def footer_rect(width: int, height: int) -> Rect:
    return Rect(0, height - FOOTER_HEIGHT, width, FOOTER_HEIGHT)


def content_rect(width: int, height: int) -> Rect:
    return Rect(
        CONTENT_PADDING,
        HEADER_HEIGHT + CONTENT_PADDING,
        width - (CONTENT_PADDING * 2),
        height - HEADER_HEIGHT - FOOTER_HEIGHT - (CONTENT_PADDING * 2),
    )
