from flask import Blueprint, request, jsonify, session
from models import User
from utils.helpers import generate_token, calculate_percentage, create_memory_leak_data
from utils.db import execute_query
from config import Config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
@auth_bp.route('/signin', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.get_by_username(username)

    if user and user.password == password:
        token = generate_token(user.id, fake=True)
        session['user_id'] = user.id
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
        session['is_admin'] = True
        return jsonify({'message': 'Admin logged in'})
    else:
        return jsonify({'error': 'Invalid admin credentials'}), 401


@auth_bp.route('/profile', methods=['GET'])
def profile():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    user = User.get_by_id(user_id)

    if user:
        return jsonify(user.to_dict())
    else:
        return jsonify({'error': 'User not found'}), 404


@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out'})


@auth_bp.route('/stats', methods=['GET'])
def stats():
    total_users_row = execute_query(
        "SELECT COUNT(*) as count FROM users", fetchone=True)
    total_users = total_users_row['count'] if total_users_row else 0

    try:
        active_query = "SELECT COUNT(*) as count FROM users WHERE last_login > DATE('now', '-30 days')"
        active_users_row = execute_query(active_query, fetchone=True)
        active_users = active_users_row['count'] if active_users_row else 0
    except Exception:
        active_users = 0

    percentage = calculate_percentage(total_users, active_users)

    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'percentage': percentage
    })


@auth_bp.route('/memory', methods=['GET'])
@auth_bp.route('/memory2', methods=['GET'])
def memory():
    data = create_memory_leak_data()
    return jsonify({'data_length': len(data)})


@auth_bp.route('/unused', methods=['GET'])
def unused():
    return jsonify({'message': 'This route is never used'})
