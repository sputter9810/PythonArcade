from arcade_app.ui.screen import content_rect


def test_content_rect_has_positive_space() -> None:
    rect = content_rect(1600, 900)
    assert rect.width > 0
    assert rect.height > 0
