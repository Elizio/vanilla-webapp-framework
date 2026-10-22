"""Tests for ProxyFix middleware with TRUST_PROXY."""
import os


def test_proxy_headers_when_trust_proxy_enabled(monkeypatch):
    """ProxyFix rewrites request.url when TRUST_PROXY=1."""
    monkeypatch.setenv('TRUST_PROXY', '1')
    monkeypatch.setenv('APP_PROFILE', 'testing')
    
    from .. import create_app
    
    app = create_app()
    client = app.test_client()
    
    response = client.get(
        '/api/health',
        headers={
            'X-Forwarded-Proto': 'https',
            'X-Forwarded-Host': 'example.com',
            'X-Forwarded-Prefix': '/vanilla-webapp-framework',
        }
    )
    
    assert response.status_code == 200
    
    with app.test_request_context(
        '/api/health',
        headers={
            'X-Forwarded-Proto': 'https',
            'X-Forwarded-Host': 'example.com',
            'X-Forwarded-Prefix': '/vanilla-webapp-framework',
        }
    ):
        from flask import request
        assert request.url.startswith('https://')
        assert 'example.com' in request.url


def test_proxy_headers_ignored_when_trust_proxy_disabled(monkeypatch):
    """ProxyFix is not applied when TRUST_PROXY is unset or 0."""
    monkeypatch.setenv('TRUST_PROXY', '0')
    monkeypatch.setenv('APP_PROFILE', 'testing')
    
    from .. import create_app
    
    app = create_app()
    client = app.test_client()
    
    response = client.get(
        '/api/health',
        headers={
            'X-Forwarded-Proto': 'https',
            'X-Forwarded-Host': 'example.com',
        }
    )
    
    assert response.status_code == 200
    
    with app.test_request_context(
        '/api/health',
        headers={
            'X-Forwarded-Proto': 'https',
            'X-Forwarded-Host': 'example.com',
        }
    ):
        from flask import request
        assert request.url.startswith('http://localhost')
