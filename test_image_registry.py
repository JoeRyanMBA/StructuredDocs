from flask import Flask

from backend.extensions import db
from backend.models import ImportDocument, ImportImage
from backend.utils.image_registry import (
    IMAGE_REGISTRY_FILENAME,
    IMAGE_REGISTRY_REVIEWER,
    build_canonical_image_payload,
    get_or_create_image_registry_document,
    register_canonical_image,
)


def create_test_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


def test_get_or_create_image_registry_document_reuses_single_registry():
    app = create_test_app()

    with app.app_context():
        db.create_all()
        first = get_or_create_image_registry_document(db, ImportDocument)
        second = get_or_create_image_registry_document(db, ImportDocument)

        assert first.id == second.id
        assert first.filename == IMAGE_REGISTRY_FILENAME
        assert first.reviewer == IMAGE_REGISTRY_REVIEWER
        assert first.status == 'approved'
        assert first.review_step == 'final_approved'


def test_register_canonical_image_creates_and_reuses_import_image_rows():
    app = create_test_app()

    with app.app_context():
        db.create_all()

        created, was_created = register_canonical_image(
            db,
            ImportImage,
            ImportDocument,
            filename='logo.png',
            original_name='Logo.png',
            public_url='/images/logo.png',
            backend_path='/tmp/logo.png',
            file_size=1234,
        )
        reused, was_created_again = register_canonical_image(
            db,
            ImportImage,
            ImportDocument,
            filename='logo.png',
            original_name='Logo.png',
            public_url='/images/logo.png',
            frontend_path='/tmp/frontend/logo.png',
        )

        assert was_created is True
        assert was_created_again is False
        assert created.id == reused.id
        assert reused.backend_path == '/tmp/logo.png'
        assert reused.frontend_path == '/tmp/frontend/logo.png'

        payload = build_canonical_image_payload(reused, include_file_exists=False)
        assert payload['id'] == reused.id
        assert payload['source'] == 'static'
        assert payload['size'] == reused.file_size
