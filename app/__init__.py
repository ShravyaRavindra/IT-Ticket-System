from flask import Flask


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "dev-secret-key"

    from app.routes.tickets import ticket_bp
    app.register_blueprint(ticket_bp)

    return app