from . import test_bp
from app.services.test.returnTables import tservice
from flask import jsonify

@test_bp.route("/tables", methods=["GET"])
def testBackend():
    try:
        result = tservice()
        return jsonify(result)
    except Exception as e:
        return {"error": str(e)}, 500
