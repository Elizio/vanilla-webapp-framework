from flask import Blueprint, jsonify
from .auth import token_required

api_bp = Blueprint('api', __name__)

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