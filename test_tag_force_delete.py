import os, json
from backend.app import create_app
from backend.models import db, Tag, Task


def setup_app(tmp_path):
    os.environ['DATABASE_URL'] = f"sqlite:///{tmp_path/'tagtest.db'}"
    os.environ['ENABLE_BLUEPRINTS'] = 'tags'
    app = create_app()
    app.config['TESTING'] = True
    return app


def test_force_delete_tag(tmp_path):
    app = setup_app(tmp_path)
    with app.app_context():
        db.create_all()
        tag = Tag(); tag.name = 'Legacy'; db.session.add(tag); db.session.commit()
        # Completed task should not block deletion (active_only default = true)
        task = Task(); task.title = 'Done Task'; task.status = 'completed'; task.tags = json.dumps(['Legacy']); db.session.add(task); db.session.commit()
        client = app.test_client()
        r = client.delete(f'/api/tags/{tag.id}')
        assert r.status_code == 200, r.get_json()
        assert r.get_json()['message'] == 'Tag deleted successfully'


def test_force_delete_active_usage(tmp_path):
    app = setup_app(tmp_path)
    with app.app_context():
        db.create_all()
        tag = Tag(); tag.name = 'ActiveTag'; db.session.add(tag); db.session.commit()
        active_task = Task(); active_task.title = 'Active Task'; active_task.status = 'in_progress'; active_task.tags = json.dumps(['ActiveTag']); db.session.add(active_task); db.session.commit()
        client = app.test_client()
        # Without force should block
        r1 = client.delete(f'/api/tags/{tag.id}')
        assert r1.status_code == 400
        # Force delete removes tag refs then deletes
        r2 = client.delete(f'/api/tags/{tag.id}?force=1')
        assert r2.status_code == 200
        body = r2.get_json()
        assert body['force'] is True
        assert body['removed_task_refs'] >= 1
