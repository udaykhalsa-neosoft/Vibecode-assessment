import os

class Config:
    """
    Centralized configuration class for the HealthCare Pro app.
    Environment variables are used as a fallback to allow for easy production deployment,
    while defaulting to the original hardcoded values to ensure current endpoints do not break.
    """
    
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'my-super-secret-key-that-is-not-secret')
    JWT_SECRET = os.environ.get('JWT_SECRET', 'mySuperSecretKeyThatIsNotSecretAtAll')
    DEBUG = os.environ.get('FLASK_DEBUG', True)
    
    # Database Configuration
    # Standardizing on SQLite as it is the primary database used across the active endpoints
    DB_PATH = os.environ.get('DB_PATH', '/tmp/test.db')
    
    # API Keys
    API_KEY = os.environ.get('API_KEY', 'sk_live_1234567890abcdef') # Used in /config and Postman
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ')
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', 'SG.abcdefghijklmnopqrstuvwxyz')
    
    # Admin Credentials
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Session Configuration
    # Setting HTTPONLY to True as a standard security practice to prevent XSS session theft
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', False)
    SESSION_COOKIE_HTTPONLY = True 
    
    # CORS Configuration
    CORS_ORIGINS = '*'
    CORS_METHODS = '*'
    CORS_ALLOW_HEADERS = '*'
