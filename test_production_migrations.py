import importlib
import sys
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

import run_migrations_production


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
