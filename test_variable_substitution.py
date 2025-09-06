import json
from backend.models import substitute_variables_in_text

def test_substitute_variables_in_text_basic():
    mapping = { 'Org': 'Acme Corp', 'Year':'2025' }
    text = 'Welcome to {{Org}} in {{Year}}.'
    assert substitute_variables_in_text(text, mapping) == 'Welcome to Acme Corp in 2025.'

def test_substitute_variables_in_text_unknown_left_intact():
    mapping = { 'Org': 'Acme' }
    text = 'Hello {{Org}} - {{Unknown}}'
    assert substitute_variables_in_text(text, mapping) == 'Hello Acme - {{Unknown}}'

def test_substitute_variables_in_text_empty_mapping():
    assert substitute_variables_in_text('Hi {{X}}', {}) == 'Hi {{X}}'

def test_substitute_variables_in_text_none_text():
    assert substitute_variables_in_text('', {'X':'Y'}) == ''
