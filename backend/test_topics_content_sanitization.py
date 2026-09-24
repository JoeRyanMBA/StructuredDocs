from backend.routes.topics import _sanitize_content


def test_topic_sanitizer_preserves_image_layout_styles():
    content = (
        '<img src="/images/example.png" '
        'style="position:absolute;z-index:-1;top:0;left:0;background:red"> text'
    )

    sanitized = _sanitize_content(content)

    assert 'position:absolute' in sanitized
    assert 'z-index:-1' in sanitized
    assert 'top:0' in sanitized
    assert 'left:0' in sanitized
    assert 'background' not in sanitized
