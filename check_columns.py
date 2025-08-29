from app_final_with_notifications_fix import create_app

app = create_app()

with app.app_context():
    from backend.models import db
    inspector = db.inspect(db.engine)
    columns = inspector.get_columns('feedback_reports')
    for col in columns:
        print(f'{col["name"]}: {col["type"]} - Nullable: {col["nullable"]} - Default: {col.get("default", "None")}')
