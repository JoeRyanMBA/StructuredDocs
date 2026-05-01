import os

from flask import Flask

from backend.routes.admin import admin_bp


class _FakeEmailService:
    def __init__(self, ok=True):
        self.ok = ok
        self.provider = 'smtp'
        self.from_email = 'no-reply@example.com'
        self.from_name = 'StructuredDocs'
        self.debug_mode = False
        self.last_error = None
        self.postmark_token = ''
        self.resend_api_key = ''
        self.smtp_server = 'smtp.example.com'
        self.smtp_port = 587
        self.sent_to = None
        self.smtp_health_ok = True
        self.smtp_health_detail = {
            'provider': 'smtp',
            'checked': True,
            'server': 'smtp.example.com',
            'port': 587,
            'useSSL': False,
            'tlsStarted': True,
            'authAttempted': True,
        }

    def reload_config(self):
        return None

    def send_test_email(self, to_email):
        self.sent_to = to_email
        return self.ok

    def check_smtp_health(self):
        return self.smtp_health_ok, self.smtp_health_detail


def _build_client(monkeypatch, service):
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(admin_bp)
    monkeypatch.setattr('backend.routes.admin.get_email_service', lambda: service)
    return app.test_client()


def test_email_status_allows_admin_api_key(monkeypatch):
    service = _FakeEmailService()
    client = _build_client(monkeypatch, service)
    monkeypatch.setenv('ADMIN_API_KEY', 'secret-token')

    response = client.get(
        '/api/admin/email-status',
        headers={'Authorization': 'Bearer secret-token'}
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['provider'] == 'smtp'
    assert payload['fromEmail'] == 'no-reply@example.com'
    assert payload['hasPostmarkToken'] is False
    assert payload['hasResendKey'] is False


def test_send_test_email_uses_shared_email_service(monkeypatch):
    service = _FakeEmailService(ok=True)
    client = _build_client(monkeypatch, service)
    monkeypatch.setenv('ADMIN_API_KEY', 'secret-token')

    response = client.post(
        '/api/admin/send-test-email',
        headers={'X-Admin-Token': 'secret-token'},
        json={'to': 'reviewer@example.com'}
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['ok'] is True
    assert payload['detail']['provider'] == 'smtp'
    assert payload['detail']['hasProviderApiKey'] is False
    assert service.sent_to == 'reviewer@example.com'


def test_email_endpoints_reject_invalid_token(monkeypatch):
    service = _FakeEmailService()
    client = _build_client(monkeypatch, service)
    monkeypatch.setenv('ADMIN_API_KEY', 'secret-token')

    response = client.get(
        '/api/admin/email-status',
        headers={'Authorization': 'Bearer wrong-token'}
    )

    assert response.status_code == 401
    assert response.get_json()['error'] == 'Unauthorized'


def test_smtp_health_check_returns_diagnostics(monkeypatch):
    service = _FakeEmailService()
    client = _build_client(monkeypatch, service)
    monkeypatch.setenv('ADMIN_API_KEY', 'secret-token')

    response = client.post(
        '/api/admin/smtp-health',
        headers={'X-Admin-Token': 'secret-token'}
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['ok'] is True
    assert payload['detail']['provider'] == 'smtp'
    assert payload['detail']['server'] == 'smtp.example.com'
    assert payload['detail']['fromEmail'] == 'no-reply@example.com'
