from flask import Blueprint, jsonify
from sqlalchemy import text

from .auth import token_required
from ..billing.entitlements import entitlement_required
from ..db_repository.database import db_session

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    ---
    tags:
      - Public
    responses:
      200:
        description: Service is healthy
      503:
        description: Database unavailable
    """
    try:
        db_session.execute(text('SELECT 1'))
    except Exception:
        return jsonify({'status': 'degraded', 'database': 'unavailable'}), 503
    return jsonify({'status': 'ok', 'database': 'ok'})


@api_bp.route('/api/public', methods=['GET'])
def public_data():
    """
    Get public data endpoint.
    ---
    tags:
      - Public
    responses:
      200:
        description: Public data retrieved successfully
        schema:
          type: object
          properties:
            info:
              type: string
    """
    return jsonify({'info': 'Hello world'})


@api_bp.route('/api/data', methods=['GET'])
@token_required
def protected_data(current_user):
    """
    Get protected data endpoint.
    ---
    tags:
      - Protected
    security:
      - Bearer: []
    responses:
      200:
        description: Protected data retrieved successfully
        schema:
          type: object
          properties:
            message:
              type: string
      401:
        description: Unauthorized access
    """
    return jsonify({'message': 'Secure data'})


@api_bp.route('/api/supporter-badge', methods=['GET'])
@token_required
@entitlement_required('supporter')
def supporter_badge(current_user):
    """
    Example feature gated by the 'supporter' entitlement.
    ---
    tags:
      - Billing
    security:
      - Bearer: []
    responses:
      200:
        description: Supporter-only content
      401:
        description: Unauthorized
      403:
        description: Entitlement required
    """
    return jsonify({'badge': 'supporter', 'message': 'Thanks for your support!'})
