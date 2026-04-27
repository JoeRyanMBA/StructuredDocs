from flask import Flask

from backend.extensions import db
from backend.models import Link
from backend.utils.link_reference_codes import backfill_link_reference_codes, resolve_link_reference_code


def create_test_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


def test_backfill_link_reference_codes_assigns_missing_values():
    app = create_test_app()

    with app.app_context():
        db.create_all()
        db.session.add_all([
            Link(title='Existing Ref', url='https://example.com/one', reference_code='LINK-AAAAAA'),
            Link(title='Missing Ref A', url='https://example.com/two'),
            Link(title='Missing Ref B', url='https://example.com/three', reference_code=''),
        ])
        db.session.commit()

        updated = backfill_link_reference_codes(db, Link)
        links = Link.query.order_by(Link.id.asc()).all()

        assert updated == 2
        assert links[0].reference_code == 'LINK-AAAAAA'
        assert links[1].reference_code.startswith('LINK-')
        assert links[2].reference_code.startswith('LINK-')
        assert links[1].reference_code != links[2].reference_code


def test_resolve_link_reference_code_normalizes_and_rejects_duplicates():
    app = create_test_app()

    with app.app_context():
        db.create_all()
        existing = Link(title='Existing Ref', url='https://example.com/one', reference_code='LINK-AAAAAA')
        db.session.add(existing)
        db.session.commit()

        assert resolve_link_reference_code(Link, ' link-bb1234 ') == 'LINK-BB1234'

        try:
            resolve_link_reference_code(Link, 'link-aaaaaa')
        except ValueError as exc:
            assert str(exc) == 'Reference code "LINK-AAAAAA" already exists'
        else:
            raise AssertionError('Expected duplicate reference code validation to fail')
