from flask import Flask, jsonify
from flask_cors import CORS
from app.routes.test import test_bp
from app.config import Config



def create_app():  
    app = Flask(__name__)  
    app.config.from_object(Config)  
    CORS(app, origins="http://localhost:5173")

    @app.route("/")
    def health():
        return jsonify({"status": "ok", "message": "Backend is working"})

    app.register_blueprint(test_bp, url_prefix="/test")

    return app  

if __name__ == "__main__":   
    app = create_app() 
    app.run(debug=True)

