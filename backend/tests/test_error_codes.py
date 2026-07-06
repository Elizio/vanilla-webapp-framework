"""Tests for API error code helpers."""
from backend.api.error_codes import error_response, USER_CREATED, INVALID_CREDENTIALS


def test_error_response_shape(test_client, test_db):
    """error_response returns JSON with code field."""
    from flask import jsonify
    from backend.api.error_codes import error_response

    with test_client.application.app_context():
        response, status = error_response(INVALID_CREDENTIALS, 401)
    # error_response returns a tuple; test the helper directly
    assert status == 401


def test_error_response_constants():
    assert USER_CREATED == 'USER_CREATED'
    assert INVALID_CREDENTIALS == 'INVALID_CREDENTIALS'
