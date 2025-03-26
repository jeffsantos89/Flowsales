import logging
from typing import Dict, Any
from flask import Flask, request, jsonify, Response
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ai.chatbot.whatsappBot import process_incoming_message
from healthcheck import HealthCheck
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from config import Config

class WhatsAppWebhookController:
    def __init__(self):
        self.app = self.create_app()
        self.setup_monitoring()
        self.setup_rate_limiting()
        self.setup_routes()
        self.setup_healthcheck()

    def create_app(self) -> Flask:
        """Initialize and configure Flask application"""
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # Handle reverse proxies
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
        
        # Configure logging
        logging.basicConfig(
            level=app.config.get('LOG_LEVEL', logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        return app

    def setup_monitoring(self) -> None:
        """Configure Sentry for error monitoring"""
        if self.app.config.get('SENTRY_DSN'):
            sentry_sdk.init(
                dsn=self.app.config['SENTRY_DSN'],
                integrations=[FlaskIntegration()],
                traces_sample_rate=1.0,
                environment=self.app.config.get('ENVIRONMENT', 'production')
            )

    def setup_rate_limiting(self) -> None:
        """Configure rate limiting"""
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )

    def setup_healthcheck(self) -> None:
        """Configure health check endpoints"""
        health = HealthCheck()
        self.app.add_url_rule("/health", "healthcheck", view_func=lambda: health.run())

    def validate_webhook_data(self, data: Dict[str, Any]) -> bool:
        """Validate incoming webhook data"""
        required_fields = ['messages', 'contacts']  # Add required fields
        return all(field in data for field in required_fields)

    def setup_routes(self) -> None:
        """Configure application routes"""
        @self.app.route("/webhook/whatsapp", methods=["POST"])
        @self.limiter.limit("100/minute")  # Rate limit per endpoint
        def whatsapp_webhook() -> Response:
            try:
                data = request.get_json(force=True)
                
                if not data:
                    self.logger.error("No JSON data received")
                    return jsonify({"error": "No JSON data received"}), 400

                if not self.validate_webhook_data(data):
                    self.logger.error("Invalid webhook data format")
                    return jsonify({"error": "Invalid data format"}), 400

                response = process_incoming_message(data)
                self.logger.info(f"Successfully processed message: {response}")
                
                return jsonify({
                    "status": "success",
                    "data": response
                }), 200

            except Exception as e:
                self.logger.exception("Error processing WhatsApp message")
                sentry_sdk.capture_exception(e)
                return jsonify({
                    "status": "error",
                    "error": "Internal server error",
                    "message": str(e) if self.app.debug else None
                }), 500

def main():
    controller = WhatsAppWebhookController()
    return controller.app

if __name__ == "__main__":
    app = main()
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5003),
        debug=app.config.get('DEBUG', False)
    )
