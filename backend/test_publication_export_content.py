import io

import pytest
from flask import Flask
from flask_jwt_extended import create_access_token

from backend.extensions import db, jwt
from backend.models import EntityTag, Publication, PublicationNode, Snippet, Tag, Topic
from backend.routes import publications
from backend.routes.publications import _select_publication_content


def test_empty_snapshot_uses_current_topic_content():
    assert _select_publication_content('', '<img src="current.png">') == '<img src="current.png">'
    assert _select_publication_content(None, 'current topic content') == 'current topic content'


def test_non_empty_snapshot_remains_authoritative():
    assert _select_publication_content('published snapshot', 'newer topic content') == 'published snapshot'


@pytest.fixture
def publication_app(tmp_path):
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{tmp_path / "publication.sqlite"}',
        JWT_SECRET_KEY='publication-testing-secret-key-at-least-32-bytes',
    )
    db.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(publications.pubs_bp)
    with app.app_context():
        db.create_all()
        admin, other = Tag(name='Admin'), Tag(name='Other')
        pub = Publication(title='Guide')
        topics = [Topic(title=title, content=title) for title in (
            'Universal', 'Admin parent', 'Universal child', 'Other child',
            'Admin grandchild', 'After parent',
        )]
        db.session.add_all([admin, other, pub, *topics])
        db.session.flush()
        nodes = [PublicationNode(publication=pub, topic=topic, position=position,
                                 title_snapshot=topic.title, content_snapshot=topic.content)
                 for position, topic in enumerate(topics)]
        nodes[2].parent = nodes[1]
        nodes[3].parent = nodes[1]
        nodes[4].parent = nodes[3]
        db.session.add_all(nodes)
        db.session.add_all([
            EntityTag(entity_type='topic', entity_id=topics[1].id, tag_id=admin.id),
            EntityTag(entity_type='topic', entity_id=topics[3].id, tag_id=other.id),
            EntityTag(entity_type='topic', entity_id=topics[4].id, tag_id=admin.id),
            EntityTag(entity_type='topic', entity_id=topics[4].id, tag_id=other.id),
        ])
        snippet = Snippet(title='Tagged snippet', content='Snippet text')
        db.session.add(snippet)
        db.session.flush()
        db.session.add(EntityTag(entity_type='snippet', entity_id=snippet.id, tag_id=admin.id))
        nodes[0].content_snapshot = f'<div class="sd-snippet-ref" data-snippet-id="{snippet.id}"></div>'
        db.session.commit()
        yield app, pub.id, admin.id, other.id
        db.session.remove()
        db.drop_all()


@pytest.mark.parametrize('endpoint', ['export/mobile-kb', 'preview/mobile-kb', 'export/pdf'])
@pytest.mark.parametrize('selection,expected,snippet_visible', [
    ('none', [('Universal', []), ('Universal child', []), ('After parent', [])], False),
    ('admin', [('Universal', []), ('Admin parent', [
        ('Universal child', []), ('Admin grandchild', []),
    ]), ('After parent', [])], True),
    ('other', [('Universal', []), ('Universal child', []), ('Other child', [
        ('Admin grandchild', []),
    ]), ('After parent', [])], False),
])
def test_exports_filter_topic_tags_and_promote_children(
    publication_app, monkeypatch, endpoint, selection, expected, snippet_visible
):
    app, pub_id, admin_id, other_id = publication_app
    captured = []

    def kb_generator(pub, tree):
        captured.append(tree)
        return 'KB'

    def pdf_generator(pub, tree, config, background):
        captured.append(tree)
        return io.BytesIO(b'%PDF test')

    monkeypatch.setattr(publications, 'generate_mobile_kb_html', kb_generator)
    monkeypatch.setattr(publications, 'generate_pdf', pdf_generator)
    tag_id = {'none': None, 'admin': admin_id, 'other': other_id}[selection]
    headers = {'Authorization': f'Bearer {create_access_token(identity="1")}'}
    response = app.test_client().get(
        f'/api/publications/{pub_id}/{endpoint}',
        query_string={'tag_ids': tag_id} if tag_id else {},
        headers=headers,
    )

    assert response.status_code == 200

    def shape(nodes):
        return [(node['title'], shape(node['children'])) for node in nodes]

    assert shape(captured[0]) == expected
    assert ('Snippet text' in captured[0][0]['content']) is snippet_visible


def test_real_exports_use_current_topic_tags_without_changing_snapshot(publication_app):
    app, pub_id, admin_id, _ = publication_app
    headers = {'Authorization': f'Bearer {create_access_token(identity="1")}'}
    client = app.test_client()
    url = f'/api/publications/{pub_id}'

    html = client.get(f'{url}/export/mobile-kb', headers=headers)
    assert html.status_code == 200
    assert 'Admin parent' not in html.get_data(as_text=True)
    assert 'Universal child' in html.get_data(as_text=True)
    assert PublicationNode.query.filter_by(publication_id=pub_id).count() == 6

    pdf = client.get(f'{url}/export/pdf', headers=headers)
    assert pdf.status_code == 200
    assert pdf.data.startswith(b'%PDF')

    assignment = EntityTag.query.filter_by(
        entity_type='topic', tag_id=admin_id,
        entity_id=Topic.query.filter_by(title='Admin parent').one().id,
    ).one()
    db.session.delete(assignment)
    db.session.commit()
    html = client.get(f'{url}/export/mobile-kb', headers=headers)
    assert 'Admin parent' in html.get_data(as_text=True)