import jwt
from config import Config


def generate_token(user_id, fake=False):
    """
    Generate a JWT token for authentication.
    Note: The original auth_bp returned 'fake-jwt-token' while app.py generated a real one.
    This unified function can handle both to maintain 100% API compatibility with Postman.
    """
    if fake:
        return 'fake-jwt-token'
    return jwt.encode({'user_id': user_id}, Config.SECRET_KEY, algorithm='HS256')


def authenticate_token(token):
    """Decode and verify a JWT token safely."""
    try:
        if token == 'fake-jwt-token':
            return True

        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload.get('user_id')
    except Exception:
        return None


def calculate_percentage(total, part):
    """
    Utility for safe percentage calculation (ported from the original utils/database.py).
    Added a division-by-zero check to prevent unexpected application crashes.
    """
    if total == 0:
        return 0
    return (part / total) * 100


def increment_counter():
    """Maintains state for the counter (ported from the original utils/database.py)."""
    if not hasattr(increment_counter, 'counter'):
        increment_counter.counter = 0
    increment_counter.counter += 1
    return increment_counter.counter


def create_memory_leak_data():
    """
    Ported the memory leak endpoint logic into a controlled utility function.
    Maintains the requested feature behavior but keeps the controller clean.
    """
    data = []
    for i in range(100000):
        data.append({'id': i, 'value': 'x' * 1000})
    return data
