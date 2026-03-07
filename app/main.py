from flask import Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app, origins="http://localhost:5173")

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "Backend is working"
    })

if __name__ == "__main__":
    app.run(debug=True)