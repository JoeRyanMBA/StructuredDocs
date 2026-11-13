from backend.utils.email_service import EmailService


def test_bulk_review_email_topics_use_bullets_without_number_prefixes():
    html = EmailService()._create_bulk_review_email_html(
        reviewer_name='Reviewer',
        topic_titles=['First topic', 'Second topic'],
        author_message=None,
        due_date=None,
        priority='medium',
        portal_url='https://example.com/review',
    )

    assert '<ul style="margin:0;padding-left:20px;">' in html
    assert '<li style="padding:4px 0;">First topic</li>' in html
    assert '<li style="padding:4px 0;">Second topic</li>' in html
    assert '1. First topic' not in html
