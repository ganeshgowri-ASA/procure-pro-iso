from app import create_app

# Create Flask app instance for Vercel
app = create_app()

# This is the WSGI entry point for Vercel
if __name__ == '__main__':
    app.run()
