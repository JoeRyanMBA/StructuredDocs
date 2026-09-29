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


def test_topic_sanitizer_preserves_watermark_opacity():
    content = '<img src="/images/example.png" style="position:absolute;z-index:-1;opacity:0.18">'

    sanitized = _sanitize_content(content)

    assert 'opacity:0.18' in sanitized


def test_topic_sanitizer_allows_only_watermark_alignment_transforms():
    safe = '<img src="/images/example.png" style="transform:translateX(-50%)">'
    unsafe = '<img src="/images/example.png" style="transform:rotate(45deg)">'

    assert 'transform:translateX(-50%)' in _sanitize_content(safe)
    assert 'transform' not in _sanitize_content(unsafe)


def test_topic_sanitizer_preserves_safe_tight_wrap_polygon_only():
    safe_content = '<img src="/images/example.png" style="float:left;shape-outside:polygon(0% 0%, 100% 0%, 100% 100%)">'
    unsafe_content = '<img src="/images/example.png" style="float:left;shape-outside:url(https://example.com/shape.png)">'
    mixed_content = '<img src="/images/example.png" style="shape-outside:url(https://example.com/shape.png);shape-outside:polygon(0% 0%, 100% 0%, 100% 100%)">'

    assert 'shape-outside:polygon' in _sanitize_content(safe_content)
    assert 'shape-outside' not in _sanitize_content(unsafe_content)
    assert 'shape-outside' not in _sanitize_content(mixed_content)
