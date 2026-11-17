import io
import sys
from contextlib import nullcontext
from contextlib import redirect_stdout
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

import run_migrations_production


class ProductionMigrationBootstrapTests(unittest.TestCase):
    def test_fresh_database_uses_migrations_without_create_all(self):
        inspector = SimpleNamespace(get_table_names=lambda: [])
        db = SimpleNamespace(
            inspect=Mock(return_value=inspector),
            engine=object(),
            create_all=Mock(),
        )
        app = SimpleNamespace(app_context=nullcontext)
        upgrade = Mock(side_effect=RuntimeError("database upgrade failed"))
        modules = {
            "backend.app": SimpleNamespace(create_app=lambda: app),
            "backend.extensions": SimpleNamespace(db=db, migrate=object()),
            "flask_migrate": SimpleNamespace(upgrade=upgrade),
        }
        output = io.StringIO()

        with unittest.mock.patch.dict(sys.modules, modules), redirect_stdout(output):
            self.assertFalse(run_migrations_production.run_migrations())

        db.inspect.assert_called_once_with(db.engine)
        db.create_all.assert_not_called()
        upgrade.assert_called_once_with(
            directory=run_migrations_production.os.path.join(
                run_migrations_production.os.path.dirname(
                    run_migrations_production.__file__
                ),
                "backend",
                "migrations",
            ),
            revision="heads",
        )
        self.assertIn("Alembic migrations will initialize the database", output.getvalue())
        self.assertIn("database upgrade failed", output.getvalue())
        self.assertNotIn("Auditing schema", output.getvalue())


if __name__ == "__main__":
    unittest.main()
