from backend.routes.publications import _select_publication_content


def test_empty_snapshot_uses_current_topic_content():
    assert _select_publication_content('', '<img src="current.png">') == '<img src="current.png">'
    assert _select_publication_content(None, 'current topic content') == 'current topic content'


def test_non_empty_snapshot_remains_authoritative():
    assert _select_publication_content('published snapshot', 'newer topic content') == 'published snapshot'