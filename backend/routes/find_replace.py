import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import (
    db, User, Topic, Collection, Project, Snippet, Task, ProjectMilestone,
    Stakeholder, ProjectStakeholder, Link, Tag, Variable, Publication,
    Review, ReviewFeedback, ReviewSequence, ReviewSequenceStep,
    HelpLink, Notification,
)

find_replace_bp = Blueprint('find_replace', __name__, url_prefix='/api/admin/find-replace')

MAX_HITS = 500

# ---------------------------------------------------------------------------
# Schema: which models/fields to search
# Each entry: (model_class, field_name, field_label, display_title_field, is_html)
# display_title_field is the attribute used as the human-readable record title.
# ---------------------------------------------------------------------------
SEARCH_SCHEMA = [
    # model                 field           label               title_field     html?
    (Topic,                 'title',        'Title',            'title',        False),
    (Topic,                 'content',      'Content',          'title',        True),
    (Collection,            'name',         'Name',             'name',         False),
    (Collection,            'description',  'Description',      'name',         False),
    (Collection,            'form_number',  'Form Number',      'name',         False),
    (Project,               'name',         'Name',             'name',         False),
    (Project,               'description',  'Description',      'name',         False),
    (Snippet,               'title',        'Title',            'title',        False),
    (Snippet,               'content',      'Content',          'title',        False),
    (Task,                  'title',        'Title',            'title',        False),
    (Task,                  'description',  'Description',      'title',        False),
    (ProjectMilestone,      'name',         'Name',             'name',         False),
    (ProjectMilestone,      'description',  'Description',      'name',         False),
    (Stakeholder,           'name',         'Name',             'name',         False),
    (Stakeholder,           'title',        'Title',            'name',         False),
    (Stakeholder,           'organization', 'Organization',     'name',         False),
    (Stakeholder,           'division',     'Division',         'name',         False),
    (Stakeholder,           'department',   'Department',       'name',         False),
    (Stakeholder,           'bio',          'Bio',              'name',         False),
    (ProjectStakeholder,    'notes',        'Notes',            'id',           False),
    (Link,                  'title',        'Title',            'title',        False),
    (Link,                  'description',  'Description',      'title',        False),
    (Link,                  'reference_code','Reference Code',  'title',        False),
    (Tag,                   'name',         'Name',             'name',         False),
    (Tag,                   'description',  'Description',      'name',         False),
    (Variable,              'name',         'Name',             'name',         False),
    (Variable,              'description',  'Description',      'name',         False),
    (Publication,           'title',        'Title',            'title',        False),
    (Publication,           'description',  'Description',      'title',        False),
    (Review,                'feedback',     'Feedback',         'id',           False),
    (Review,                'review_notes', 'Review Notes',     'id',           False),
    (Review,                'author_message','Author Message',  'id',           False),
    (ReviewFeedback,        'comment',      'Comment',          'id',           False),
    (ReviewFeedback,        'suggested_text','Suggested Text',  'id',           False),
    (ReviewFeedback,        'rationale',    'Rationale',        'id',           False),
    (ReviewFeedback,        'author_response','Author Response','id',           False),
    (ReviewSequence,        'name',         'Name',             'name',         False),
    (ReviewSequence,        'description',  'Description',      'name',         False),
    (ReviewSequenceStep,    'name',         'Name',             'name',         False),
    (ReviewSequenceStep,    'instructions', 'Instructions',     'name',         False),
    (HelpLink,              'title',        'Title',            'title',        False),
    (HelpLink,              'description',  'Description',      'title',        False),
    (Notification,          'title',        'Title',            'title',        False),
    (Notification,          'message',      'Message',          'title',        False),
]

# Map model class name → list of schema entries for that model
_SCHEMA_BY_MODEL = {}
for _entry in SEARCH_SCHEMA:
    _SCHEMA_BY_MODEL.setdefault(_entry[0].__name__, []).append(_entry)

CONTEXT_CHARS = 80


def _require_admin():
    uid = get_jwt_identity()
    try:
        uid = int(uid)
    except (TypeError, ValueError):
        pass
    user = User.query.get(uid) if uid is not None else None
    if not user or user.role != 'admin':
        return None, (jsonify({'error': 'Admin access required'}), 403)
    return user, None


def _strip_html(html: str) -> str:
    """Very lightweight HTML tag stripper for context display."""
    return re.sub(r'<[^>]+>', ' ', html or '')


def _build_context(text: str, match: re.Match, is_html: bool) -> dict:
    """Return context_before, match_text, context_after from the plain-text version."""
    plain = _strip_html(text) if is_html else (text or '')
    start, end = match.start(), match.end()

    if is_html:
        # Re-find the match in plain text (positions differ after stripping)
        try:
            plain_match = re.search(re.escape(match.group()), plain, re.IGNORECASE)
            if plain_match:
                start, end = plain_match.start(), plain_match.end()
            else:
                start, end = 0, min(len(plain), 100)
        except re.error:
            start, end = 0, min(len(plain), 100)

    return {
        'context_before': plain[max(0, start - CONTEXT_CHARS):start],
        'match_text': plain[start:end],
        'context_after': plain[end:end + CONTEXT_CHARS],
    }


def _compile_pattern(pattern: str, flags_cfg: dict):
    """Compile regex; returns (pattern_obj, error_str)."""
    flags = 0
    if flags_cfg.get('ignoreCase', True):
        flags |= re.IGNORECASE
    if flags_cfg.get('multiline'):
        flags |= re.MULTILINE
    if flags_cfg.get('dotall'):
        flags |= re.DOTALL
    try:
        return re.compile(pattern, flags), None
    except re.error as e:
        return None, str(e)


@find_replace_bp.route('/search', methods=['POST'])
@jwt_required()
def search():
    _, err = _require_admin()
    if err:
        return err

    data = request.get_json() or {}
    pattern_str = (data.get('pattern') or '').strip()
    if not pattern_str:
        return jsonify({'error': 'Pattern is required'}), 400

    flags_cfg = data.get('flags', {})
    compiled, err_msg = _compile_pattern(pattern_str, flags_cfg)
    if compiled is None:
        return jsonify({'error': f'Invalid regex: {err_msg}'}), 400

    # Which models the client wants to search (default: all)
    scope = data.get('scope') or [e[0].__name__ for e in SEARCH_SCHEMA]

    hits = []
    truncated = False

    for model_cls, field_name, field_label, title_field, is_html in SEARCH_SCHEMA:
        model_name = model_cls.__name__
        if model_name not in scope:
            continue
        if len(hits) >= MAX_HITS:
            truncated = True
            break

        col = getattr(model_cls, field_name, None)
        if col is None:
            continue

        try:
            records = model_cls.query.filter(col.isnot(None)).all()
        except Exception:
            continue

        for record in records:
            if len(hits) >= MAX_HITS:
                truncated = True
                break
            value = getattr(record, field_name, None)
            if not value:
                continue

            search_text = _strip_html(value) if is_html else value
            match = compiled.search(search_text)
            if not match:
                continue

            title_val = getattr(record, title_field, None)
            record_title = str(title_val) if title_val is not None else f'{model_name} #{record.id}'

            ctx = _build_context(value, match, is_html)
            hits.append({
                'model': model_name,
                'record_id': record.id,
                'record_title': record_title,
                'field': field_name,
                'field_label': field_label,
                'is_html': is_html,
                **ctx,
            })

    return jsonify({'hits': hits, 'truncated': truncated, 'total': len(hits)}), 200


@find_replace_bp.route('/replace', methods=['POST'])
@jwt_required()
def replace():
    _, err = _require_admin()
    if err:
        return err

    data = request.get_json() or {}
    pattern_str = (data.get('pattern') or '').strip()
    replacement = data.get('replacement', '')
    selected_hits = data.get('hits', [])  # [{model, record_id, field}, ...]

    if not pattern_str:
        return jsonify({'error': 'Pattern is required'}), 400
    if not selected_hits:
        return jsonify({'error': 'No hits selected'}), 400

    flags_cfg = data.get('flags', {})
    compiled, err_msg = _compile_pattern(pattern_str, flags_cfg)
    if compiled is None:
        return jsonify({'error': f'Invalid regex: {err_msg}'}), 400

    # Build a lookup: model_name → schema entries
    replaced_count = 0
    errors = []

    # Group hits by (model, record_id) to batch field updates per record
    from collections import defaultdict
    grouped: dict = defaultdict(list)
    for h in selected_hits:
        key = (h.get('model'), h.get('record_id'))
        grouped[key].append(h.get('field'))

    for (model_name, record_id), fields in grouped.items():
        entries = _SCHEMA_BY_MODEL.get(model_name, [])
        if not entries:
            errors.append(f'Unknown model: {model_name}')
            continue

        model_cls = entries[0][0]
        try:
            record = model_cls.query.get(record_id)
            if record is None:
                errors.append(f'{model_name} #{record_id} not found')
                continue

            for field_name in fields:
                field_entry = next(
                    (e for e in entries if e[1] == field_name), None
                )
                if field_entry is None:
                    errors.append(f'Unknown field {field_name} on {model_name}')
                    continue

                current_value = getattr(record, field_name, None)
                if not current_value:
                    continue

                new_value = compiled.sub(replacement, current_value)
                if new_value != current_value:
                    setattr(record, field_name, new_value)
                    replaced_count += 1

            db.session.add(record)
        except Exception as e:
            errors.append(f'Error updating {model_name} #{record_id}: {str(e)}')
            db.session.rollback()
            continue

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database commit failed: {str(e)}'}), 500

    return jsonify({'replaced_count': replaced_count, 'errors': errors}), 200
