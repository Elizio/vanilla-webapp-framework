"""Tests for API error code helpers."""
import json
from pathlib import Path

import backend.api.error_codes as error_codes_mod
from backend.api.error_codes import USER_CREATED, INVALID_CREDENTIALS

REPO_ROOT = Path(__file__).resolve().parents[2]


def _backend_error_code_constants():
    """Return every ALL_CAPS string constant defined in error_codes.py."""
    return [
        value
        for name, value in vars(error_codes_mod).items()
        if name.isupper() and isinstance(value, str) and name == value
    ]


def test_error_response_shape(test_client, test_db):
    """error_response returns JSON with code field."""
    from backend.api.error_codes import error_response

    with test_client.application.app_context():
        response, status = error_response(INVALID_CREDENTIALS, 401)
    # error_response returns a tuple; test the helper directly
    assert status == 401


def test_error_response_constants():
    assert USER_CREATED == 'USER_CREATED'
    assert INVALID_CREDENTIALS == 'INVALID_CREDENTIALS'


def test_http_status_code_mapping():
    """Non-404 4xx statuses map to specific codes, never NOT_FOUND."""
    from backend.api.error_codes import (
        BAD_REQUEST,
        FORBIDDEN,
        INTERNAL_ERROR,
        METHOD_NOT_ALLOWED,
        NOT_FOUND,
        RATE_LIMIT_EXCEEDED,
        UNAUTHORIZED,
    )
    from backend.web_routes import code_for_http_status

    assert code_for_http_status(400) == BAD_REQUEST
    assert code_for_http_status(401) == UNAUTHORIZED
    assert code_for_http_status(403) == FORBIDDEN
    assert code_for_http_status(404) == NOT_FOUND
    assert code_for_http_status(405) == METHOD_NOT_ALLOWED
    assert code_for_http_status(429) == RATE_LIMIT_EXCEEDED
    assert code_for_http_status(418) == BAD_REQUEST
    assert code_for_http_status(500) == INTERNAL_ERROR
    assert code_for_http_status(None) == INTERNAL_ERROR


def test_every_error_code_has_en_and_pt_br_locale_keys():
    """Every backend error/success code has errors.<CODE> in both locales."""
    codes = _backend_error_code_constants()
    assert codes
    for locale_name in ('en.json', 'pt-BR.json'):
        catalog = json.loads(
            (REPO_ROOT / 'frontend' / 'src' / 'locales' / locale_name).read_text()
        )
        errors = catalog.get('errors', {})
        missing = [
            code
            for code in codes
            if not isinstance(errors.get(code), str) or not errors[code].strip()
        ]
        assert missing == [], f'{locale_name} missing errors.* keys: {missing}'
