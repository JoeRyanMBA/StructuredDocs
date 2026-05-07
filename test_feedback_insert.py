from backend.app import create_app

app = create_app()

with app.app_context():
    from backend.models import FeedbackReport, db
    
    # Try to create a feedback report
    try:
        feedback = FeedbackReport(
            report_type='other',
            page='/test',
            message='Test feedback'
        )
        db.session.add(feedback)
        db.session.commit()
        print('Feedback created successfully with ID:', feedback.id)
    except Exception as e:
        print('Error creating feedback:', str(e))
        db.session.rollback()
