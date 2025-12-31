"""
Procure-Pro-ISO - Procurement Management System
Main Flask Application Entry Point
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration
from config.settings import Config

# Import API routes
from api.routes import api_bp

# Import database connection
from database.connection import init_db, close_db


def create_app(config_class=Config):
    """
    Application factory for creating Flask app instances.

    Args:
        config_class: Configuration class to use

    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Initialize database connection
    init_db(app)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for Railway deployment."""
        return jsonify({
            'status': 'healthy',
            'service': 'procure-pro-iso',
            'version': '1.0.0'
        }), 200

    # Root endpoint
    @app.route('/')
    def index():
        """Root endpoint with API information."""
        return jsonify({
            'name': 'Procure-Pro-ISO API',
            'version': '1.0.0',
            'description': 'Procurement Management System with ISO Compliance',
            'documentation': '/api/v1/docs',
            'endpoints': {
                'projects': '/api/v1/projects',
                'rfqs': '/api/v1/rfqs',
                'vendors': '/api/v1/vendors',
                'items': '/api/v1/items',
                'bids': '/api/v1/bids',
                'purchase_orders': '/api/v1/purchase-orders',
                'tbe_evaluations': '/api/v1/tbe-evaluations'
            }
        }), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500

    # Teardown
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        close_db()

    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'

    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║           Procure-Pro-ISO API Server                     ║
    ║                                                          ║
    ║   Running on: http://0.0.0.0:{port}                       ║
    ║   Environment: {'Development' if debug else 'Production'}                           ║
    ║   Version: 1.0.0                                         ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    app.run(host='0.0.0.0', port=port, debug=debug)
