import pytest

# Provide a session-scoped token fixture for tests that need a review token.
# This calls the helper in test_review_system.py which attempts to generate
# a token by hitting the running backend at http://localhost:5050.
def _generate_token():
    try:
        # Import locally to avoid import-time side effects for other tests
        from test_review_system import test_token_generation
        return test_token_generation()
    except Exception:
        return None


@pytest.fixture(scope="session")
def token():
    return _generate_token()
