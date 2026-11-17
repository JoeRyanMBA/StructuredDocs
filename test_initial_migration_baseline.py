import importlib
from pathlib import Path
import unittest

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations


MIGRATION_PATH = (
    Path(__file__).parent
    / "backend/migrations/versions/b95a3c29dcb3_initial_migration_from_clean_models.py"
)
spec = importlib.util.spec_from_file_location("initial_migration", MIGRATION_PATH)
MIGRATION = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MIGRATION)


class InitialMigrationBaselineTests(unittest.TestCase):
    def test_empty_database_can_apply_baseline(self):
        engine = sa.create_engine("sqlite://")

        try:
            with engine.begin() as connection:
                with Operations.context(MigrationContext.configure(connection)):
                    MIGRATION.upgrade()
                self.assertTrue(MIGRATION._baseline_schema_is_present(connection))
                with Operations.context(MigrationContext.configure(connection)):
                    MIGRATION.upgrade()
        finally:
            engine.dispose()

    def test_complete_existing_baseline_is_not_recreated(self):
        engine = sa.create_engine("sqlite://")
        metadata = sa.MetaData()
        tables = {}

        for table_name, column_names in MIGRATION._BASELINE_COLUMNS.items():
            primary_key = MIGRATION._BASELINE_PRIMARY_KEYS[table_name]
            columns = [
                sa.Column(name, sa.Integer, primary_key=name in primary_key)
                for name in column_names
            ]
            tables[table_name] = sa.Table(table_name, metadata, *columns)

        for table_name, constraints in MIGRATION._BASELINE_UNIQUE_CONSTRAINTS.items():
            for columns in constraints:
                sa.UniqueConstraint(*(tables[table_name].c[name] for name in columns))

        for table_name, constraints in MIGRATION._BASELINE_FOREIGN_KEYS.items():
            for columns, referred_table, referred_columns in constraints:
                sa.ForeignKeyConstraint(
                    [tables[table_name].c[name] for name in columns],
                    [tables[referred_table].c[name] for name in referred_columns],
                )

        try:
            metadata.create_all(engine)
            with engine.begin() as connection:
                with Operations.context(MigrationContext.configure(connection)):
                    MIGRATION.upgrade()
                self.assertTrue(MIGRATION._baseline_schema_is_present(connection))
        finally:
            engine.dispose()

    def test_partial_existing_baseline_fails_without_replaying_ddl(self):
        engine = sa.create_engine("sqlite://")
        metadata = sa.MetaData()
        sa.Table(
            "import_documents",
            metadata,
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("filename", sa.String),
            sa.Column("source_type", sa.String),
        )

        try:
            metadata.create_all(engine)
            with engine.begin() as connection:
                with Operations.context(MigrationContext.configure(connection)):
                    with self.assertRaisesRegex(RuntimeError, "partial pre-existing schema"):
                        MIGRATION.upgrade()
                self.assertIn("import_documents", sa.inspect(connection).get_table_names())
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
