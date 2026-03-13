from flask import Blueprint, jsonify
from app.services import test as tService
test_bp = Blueprint("test", __name__)

@test_bp.route("/", methods=["GET"])
def testBackend():
     try: 
          result = tService.test()
          return jsonify(result)
     except Exception as e: 
          return jsonify({"error": str(e)}), 500 


