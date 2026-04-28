from backend.utils.email_service import EmailService


class _FakeSMTP:
    instances = []

    def __init__(self, host, port, *_args, **_kwargs):
        self.host = host
        self.port = port
        self.messages = []
        self.quit_called = False
        _FakeSMTP.instances.append(self)

    def starttls(self):
        return None

    def login(self, *_args, **_kwargs):
        return None

    def send_message(self, msg):
        self.messages.append(msg)

    def quit(self):
        self.quit_called = True


def test_smtp_provider_alias_uses_smtp_delivery(monkeypatch):
    _FakeSMTP.instances.clear()
    monkeypatch.setenv('EMAIL_PROVIDER', 'smtp')
    monkeypatch.setenv('SMTP_SERVER', 'smtp.example.com')
    monkeypatch.setenv('SMTP_PORT', '587')
    monkeypatch.setenv('SMTP_USE_SSL', 'false')
    monkeypatch.delenv('SMTP_USERNAME', raising=False)
    monkeypatch.delenv('SMTP_PASSWORD', raising=False)
    monkeypatch.setenv('EMAIL_DEBUG', 'false')

    service = EmailService()

    def _unexpected_provider_send(*_args, **_kwargs):
        raise AssertionError('Provider API path should not be used for EMAIL_PROVIDER=smtp')

    monkeypatch.setattr(EmailService, '_send_via_provider', _unexpected_provider_send)
    monkeypatch.setattr('backend.utils.email_service.smtplib.SMTP', _FakeSMTP)
    monkeypatch.setattr('backend.utils.email_service.smtplib.SMTP_SSL', _FakeSMTP)

    assert service.provider == ''
    assert service._send_email(
        'reviewer@example.com',
        'Subject',
        '<p>Hello</p>',
        'Hello',
    ) is True

    assert len(_FakeSMTP.instances) == 1
    smtp_client = _FakeSMTP.instances[0]
    assert smtp_client.host == 'smtp.example.com'
    assert smtp_client.port == 587
    assert len(smtp_client.messages) == 1
    assert smtp_client.messages[0]['To'] == 'reviewer@example.com'
    assert smtp_client.quit_called is True
