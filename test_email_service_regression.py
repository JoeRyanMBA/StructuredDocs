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


def test_legacy_smtp_env_aliases_and_sender_fallback(monkeypatch):
    monkeypatch.delenv('SMTP_SERVER', raising=False)
    monkeypatch.setenv('SMTP_HOST', 'smtp.legacy.example.com')
    monkeypatch.delenv('SMTP_USERNAME', raising=False)
    monkeypatch.setenv('SMTP_USER', 'legacy-user')
    monkeypatch.setenv('SMTP_PASSWORD', 'legacy-pass')
    monkeypatch.delenv('FROM_EMAIL', raising=False)
    monkeypatch.delenv('DEFAULT_FROM_EMAIL', raising=False)
    monkeypatch.setenv('MAIL_DEFAULT_SENDER', 'StructuredDocs <noreply@legacy.example.com>')

    service = EmailService()

    assert service.smtp_server == 'smtp.legacy.example.com'
    assert service.smtp_username == 'legacy-user'
    assert service.from_email == 'noreply@legacy.example.com'


def test_email_layout_uses_background_free_header():
    service = EmailService()

    html = service._email_layout('Review Request', '<p>Hello</p>', 'https://example.com')

    assert 'background:#005B6E' not in html
    assert 'color:#1f2933' in html
    assert 'border-radius:8px;' in html
    assert 'border-top:none' not in html
    assert 'align="left" style="width:220px;padding-right:16px;"' in html
    assert 'align="right"' in html
    assert 'margin-bottom:10px' not in html


def test_sequential_review_request_email_explains_sme_gate():
    service = EmailService()

    html = service._create_review_request_email_html(
        'Reviewer Name',
        'Topic Title',
        'Author Name',
        None,
        'https://example.com/review/token',
        is_sequential=True,
        sequence_position=1,
        total_reviewers=3,
        base_url='https://example.com',
    )
    text = service._create_review_request_email_text(
        'Reviewer Name',
        'Topic Title',
        'Author Name',
        None,
        'https://example.com/review/token',
        is_sequential=True,
        sequence_position=1,
        total_reviewers=3,
    )

    explanation = (
        'The sequential review process gets feedback or approval from a '
        'Subject Matter Expert (SME) before other feedback.'
    )
    follow_on = (
        'This step ensures any technical elements or procedures are correct '
        'before getting feedback or approval from other reviewers.'
    )

    assert explanation in html
    assert follow_on in html
    assert explanation in text
    assert follow_on in text
