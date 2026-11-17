import importlib
import os
import sys
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

import run_migrations_production


@pytest.fixture
def postgres_migration_app():
    url = os.environ.get("TEST_POSTGRES_URL")
    if not url:
        pytest.skip("Set TEST_POSTGRES_URL to run PostgreSQL migration regressions")

    from flask import Flask
    from backend.extensions import db, migrate
    from backend import models  # noqa: F401

    schema = f"migration_test_{uuid4().hex}"
    engine = sa.create_engine(url)
    with engine.begin() as connection:
        connection.execute(sa.schema.CreateSchema(schema))
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=url,
        SQLALCHEMY_ENGINE_OPTIONS={"connect_args": {"options": f"-csearch_path={schema}"}},
    )
    db.init_app(app)
    migrate.init_app(app, db)
    try:
        with app.app_context():
            db.create_all()
            try:
                yield db
            finally:
                db.session.remove()
                db.engine.dispose()
    finally:
        with engine.begin() as connection:
            connection.execute(sa.schema.DropSchema(schema, cascade=True))
        engine.dispose()


@pytest.mark.parametrize("recorded_base", [False, True])
def test_postgres_upgrade_replays_legacy_schema_without_data_loss(
    postgres_migration_app, recorded_base
):
    from flask_migrate import upgrade

    db = postgres_migration_app
    directory = str(Path(__file__).parent / "backend" / "migrations")
    with db.engine.begin() as connection:
        connection.execute(sa.text(
            "INSERT INTO publications (id, title) VALUES (1, 'Existing publication')"
        ))
        connection.execute(sa.text(
            "INSERT INTO topics (id, title, status) VALUES (1, 'Approved topic', 'approved')"
        ))
        connection.execute(sa.text(
            "INSERT INTO system_settings (key, value) VALUES ('export_html_logo', 'existing.svg')"
        ))
        connection.execute(sa.text("ALTER TABLE publications DROP COLUMN branding_template_name"))
        connection.execute(sa.text("ALTER TABLE users DROP COLUMN last_seen"))
        if recorded_base:
            connection.execute(sa.text(
                "CREATE TABLE alembic_version (version_num VARCHAR(32) PRIMARY KEY)"
            ))
            connection.execute(sa.text(
                "INSERT INTO alembic_version VALUES ('b95a3c29dcb3')"
            ))

    upgrade(directory=directory, revision="heads")
    upgrade(directory=directory, revision="heads")

    with db.engine.connect() as connection:
        assert connection.execute(sa.text(
            "SELECT title, branding_template_name FROM publications WHERE id = 1"
        )).one() == ("Existing publication", None)
        assert connection.execute(sa.text(
            "SELECT title, status FROM topics WHERE id = 1"
        )).one() == ("Approved topic", "approved")
        assert connection.execute(sa.text(
            "SELECT value FROM system_settings WHERE key = 'export_html_logo'"
        )).scalar_one() == "existing.svg"
        assert "last_seen" in {
            column["name"] for column in sa.inspect(connection).get_columns("users")
        }
        assert connection.execute(sa.text(
            "SELECT version_num FROM alembic_version"
        )).scalars().all() == ["20261112_remove_variable_scope"]


def test_initial_postgres_migration_reuses_existing_enum_types(postgres_migration_app):
    db = postgres_migration_app
    migration = importlib.import_module(
        "backend.migrations.versions.b95a3c29dcb3_initial_migration_from_clean_models"
    )
    with db.engine.begin() as connection:
        connection.execute(sa.text("DROP TABLE import_documents CASCADE"))
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
            migration.upgrade()
        connection.execute(sa.text(
            "INSERT INTO import_documents "
            "(filename, source_type, status, review_step, created_at) "
            "VALUES ('original.docx', 'word', 'staging', 'pending', CURRENT_TIMESTAMP)"
        ))
        assert connection.execute(sa.text(
            "SELECT filename FROM import_documents"
        )).scalar_one() == "original.docx"


def test_migration_failure_stops_before_schema_repairs(monkeypatch, capsys):
    inspector = SimpleNamespace(get_table_names=lambda: ["publications"])
    db = SimpleNamespace(inspect=Mock(return_value=inspector), engine=object())
    app = SimpleNamespace(app_context=nullcontext)
    upgrade = Mock(side_effect=RuntimeError("database upgrade failed"))
    monkeypatch.setitem(
        sys.modules,
        "backend.app",
        SimpleNamespace(create_app=lambda: app),
    )
    monkeypatch.setitem(
        sys.modules,
        "backend.extensions",
        SimpleNamespace(db=db, migrate=object()),
    )
    monkeypatch.setitem(
        sys.modules,
        "flask_migrate",
        SimpleNamespace(upgrade=upgrade),
    )

    assert run_migrations_production.run_migrations() is False

    upgrade.assert_called_once()
    db.inspect.assert_called_once_with(db.engine)
    output = capsys.readouterr().out
    assert "database upgrade failed" in output
    assert "Auditing schema" not in output


def test_branding_migration_preserves_publications_and_can_be_repeated():
    migration = importlib.import_module(
        "backend.migrations.versions.20260826_add_branding_template_to_publications"
    )
    engine = sa.create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            connection.execute(sa.text(
                "CREATE TABLE publications (id INTEGER PRIMARY KEY, title VARCHAR(200))"
            ))
            connection.execute(sa.text(
                "INSERT INTO publications (id, title) VALUES (1, 'Existing publication')"
            ))
            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()
                assert connection.execute(sa.text(
                    "SELECT title, branding_template_name FROM publications WHERE id = 1"
                )).one() == ("Existing publication", None)
                connection.execute(sa.text(
                    "UPDATE publications SET branding_template_name = 'existing-brand' WHERE id = 1"
                ))
                migration.upgrade()
                assert connection.execute(sa.text(
                    "SELECT title, branding_template_name FROM publications WHERE id = 1"
                )).one() == ("Existing publication", "existing-brand")
    finally:
        engine.dispose()
