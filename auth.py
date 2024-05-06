from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask import Blueprint, request, jsonify
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.find_by_username(username)
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify({'token': access_token})
    return jsonify({'error': 'Invalid credentials'}), 401
