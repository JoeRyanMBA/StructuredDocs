import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from sqlalchemy import event

from backend.extensions import db, jwt
from backend.models import Variable, VariableValue
from backend.routes.variables import variables_bp


@pytest.fixture
def variables_app(tmp_path):
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{tmp_path / "variables.sqlite"}',
        JWT_SECRET_KEY='variable-testing-secret-key-at-least-32-bytes',
    )
    db.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(variables_bp)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def auth_headers():
    return {'Authorization': f'Bearer {create_access_token(identity="1")}'}


def test_create_variable_with_initial_values_and_default(variables_app):
    response = variables_app.test_client().post(
        '/api/variables',
        json={
            'name': 'Organization',
            'slug': 'organization',
            'initial_values': [
                {'value': '  Acme  ', 'is_default': True},
                {'value': 'Example Inc', 'is_default': False},
            ],
        },
        headers=auth_headers(),
    )

    assert response.status_code == 201
    result = response.get_json()
    assert [(value['value'], value['is_default']) for value in result['values']] == [
        ('Acme', True),
        ('Example Inc', False),
    ]
    assert Variable.query.count() == 1
    assert VariableValue.query.count() == 2


def test_create_variable_without_initial_values_remains_supported(variables_app):
    response = variables_app.test_client().post(
        '/api/variables',
        json={'name': 'Organization', 'slug': 'organization'},
        headers=auth_headers(),
    )

    assert response.status_code == 201
    assert response.get_json()['values'] == []


@pytest.mark.parametrize(
    'initial_values',
    [
        [{'value': 'Acme', 'is_default': True}, {'value': 'Example Inc', 'is_default': True}],
        [{'value': 'Acme'}, {'value': 'Acme'}],
    ],
)
def test_invalid_initial_values_do_not_create_variable(variables_app, initial_values):
    response = variables_app.test_client().post(
        '/api/variables',
        json={
            'name': 'Organization',
            'slug': 'organization',
            'initial_values': initial_values,
        },
        headers=auth_headers(),
    )

    assert response.status_code == 400
    assert Variable.query.count() == 0


def test_initial_value_write_failure_rolls_back_variable(variables_app):
    def fail_value_insert(mapper, connection, target):
        raise RuntimeError('simulated value insert failure')

    event.listen(VariableValue, 'before_insert', fail_value_insert)
    try:
        response = variables_app.test_client().post(
            '/api/variables',
            json={
                'name': 'Organization',
                'slug': 'organization',
                'initial_values': [{'value': 'Acme'}],
            },
            headers=auth_headers(),
        )
    finally:
        event.remove(VariableValue, 'before_insert', fail_value_insert)

    assert response.status_code == 500
    assert Variable.query.count() == 0
    assert VariableValue.query.count() == 0
