from app_final_with_notifications_fix import create_app

app = create_app()

with app.app_context():
    from backend.models import FeedbackReport
    try:
        reports = FeedbackReport.query.limit(5).all()
        print(f'Found {len(reports)} feedback reports')
        for report in reports:
            print(f'ID: {report.id}, Type: {report.report_type}, Status: {report.status}')
    except Exception as e:
        print(f'Error querying feedback: {e}')
