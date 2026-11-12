from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from ..models import Stakeholder, User, db


def current_review_stakeholder(create=False):
    user = db.session.get(User, get_jwt_identity())
    if not user or not user.active:
        return None, (jsonify({'error': 'The current user account is unavailable.'}), 401)

    email = user.email.strip().lower()
    if not email:
        return None, (jsonify({'error': 'Your account needs an email address to use reviews.'}), 409)
    if User.query.filter(func.lower(func.trim(User.email)) == email, User.id != user.id).first():
        return None, (jsonify({'error': 'Multiple accounts match your email. Contact an administrator.'}), 409)

    def matching_stakeholders():
        return Stakeholder.query.filter(func.lower(func.trim(Stakeholder.email)) == email).limit(2).all()

    matches = matching_stakeholders()
    if len(matches) > 1:
        return None, (jsonify({'error': 'Multiple stakeholders match your account email. Contact an administrator.'}), 409)
    if matches:
        return matches[0], None
    if not create:
        return None, None

    values = {'name': user.name, 'email': user.email.strip(), 'role': 'author', 'can_review': False, 'active': True}
    dialect = db.session.get_bind().dialect.name
    if dialect in ('postgresql', 'sqlite'):
        insert = postgresql_insert if dialect == 'postgresql' else sqlite_insert
        db.session.execute(insert(Stakeholder).values(**values).on_conflict_do_nothing(index_elements=['email']))
        matches = matching_stakeholders()
        if len(matches) == 1:
            return matches[0], None
        if len(matches) > 1:
            return None, (jsonify({'error': 'Multiple stakeholders match your account email. Contact an administrator.'}), 409)
        raise RuntimeError('Could not create or resolve the requester stakeholder')
    stakeholder = Stakeholder(**values)
    db.session.add(stakeholder)
    db.session.flush()
    return stakeholder, None
