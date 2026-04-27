import random
import string

from sqlalchemy import func, or_


REFERENCE_CODE_PREFIX = 'LINK'
REFERENCE_CODE_LENGTH = 6
REFERENCE_CODE_ALPHABET = string.ascii_uppercase + string.digits


def normalize_reference_code(reference_code):
    if reference_code is None:
        return None

    normalized = reference_code.strip().upper()
    return normalized or None


def generate_unique_link_reference_code(link_model, *, prefix=REFERENCE_CODE_PREFIX, length=REFERENCE_CODE_LENGTH, max_attempts=50):
    for _ in range(max_attempts):
        suffix = ''.join(random.choices(REFERENCE_CODE_ALPHABET, k=length))
        candidate = f'{prefix}-{suffix}'
        if not link_model.query.filter_by(reference_code=candidate).first():
            return candidate

    raise RuntimeError('Unable to generate a unique reference code for link')


def resolve_link_reference_code(link_model, requested_reference_code=None, *, exclude_link_id=None):
    normalized = normalize_reference_code(requested_reference_code)
    if normalized is None:
        return generate_unique_link_reference_code(link_model)

    existing = link_model.query.filter_by(reference_code=normalized).first()
    if existing and existing.id != exclude_link_id:
        raise ValueError(f'Reference code "{normalized}" already exists')

    return normalized


def assign_missing_link_reference_code(link, link_model):
    if normalize_reference_code(link.reference_code):
        link.reference_code = normalize_reference_code(link.reference_code)
        return False

    link.reference_code = generate_unique_link_reference_code(link_model)
    return True


def backfill_link_reference_codes(db, link_model):
    links_missing_codes = (
        link_model.query
        .filter(or_(link_model.reference_code.is_(None), func.trim(link_model.reference_code) == ''))
        .order_by(link_model.id.asc())
        .all()
    )

    updated = 0
    for link in links_missing_codes:
        if assign_missing_link_reference_code(link, link_model):
            updated += 1

    if updated:
        db.session.commit()

    return updated
