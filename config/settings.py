"""
Application Configuration Settings
Defines configuration classes for different environments
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class with default settings."""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False

    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        # Railway uses postgres:// but SQLAlchemy needs postgresql://
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or (
        f"postgresql://"
        f"{os.environ.get('PGUSER', 'postgres')}:"
        f"{os.environ.get('PGPASSWORD', 'password')}@"
        f"{os.environ.get('PGHOST', 'localhost')}:"
        f"{os.environ.get('PGPORT', '5432')}/"
        f"{os.environ.get('PGDATABASE', 'procure_pro_iso')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

    # API Settings
    API_VERSION = os.environ.get('API_VERSION', 'v1')
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100/hour')

    # File Upload
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = set(
        os.environ.get('ALLOWED_EXTENSIONS', 'pdf,xlsx,xls,csv,doc,docx').split(',')
    )

    # JWT Authentication
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    )

    # Redis Cache
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@procure-pro-iso.com')

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', 'json')

    # Procurement System Settings
    DEFAULT_CURRENCY = os.environ.get('DEFAULT_CURRENCY', 'USD')
    DEFAULT_VALIDITY_DAYS = int(os.environ.get('DEFAULT_VALIDITY_DAYS', 30))

    # TBE Weights
    TBE_WEIGHT_PRICE = float(os.environ.get('TBE_WEIGHT_PRICE', 0.40))
    TBE_WEIGHT_QUALITY = float(os.environ.get('TBE_WEIGHT_QUALITY', 0.25))
    TBE_WEIGHT_DELIVERY = float(os.environ.get('TBE_WEIGHT_DELIVERY', 0.20))
    TBE_WEIGHT_COMPLIANCE = float(os.environ.get('TBE_WEIGHT_COMPLIANCE', 0.15))


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False

    # Ensure secret key is set in production
    @property
    def SECRET_KEY(self):
        key = os.environ.get('SECRET_KEY')
        if not key:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        return key


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = True

    # Use separate test database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL',
        'postgresql://postgres:password@localhost:5432/procure_pro_iso_test'
    )

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
