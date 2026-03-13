from . import test_bp
from app.services.test.returnTables import tservice


@test_bp.route("/tables", methods=["GET"])
def testBackend():
    try:
        result = tservice()
        return result
    except Exception as e:
        return {"error": str(e)}, 500
