from flask import Blueprint, jsonify
from flasgger import swag_from
from .auth import token_required

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/public', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Public data retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'info': {'type': 'string'}
                }
            }
        }
    }
})
def public_data():
    return jsonify({'info': 'Hello world'})

@api_bp.route('/api/data', methods=['GET'])
@token_required
@swag_from({
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Protected data retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        401: {
            'description': 'Unauthorized access'
        }
    }
})
def protected_data(current_user):
    return jsonify({'message': 'Secure data'}) 