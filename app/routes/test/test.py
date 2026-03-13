from . import test_bp

@test_bp.route("/")
def health():
    return {"status": "ok", "message": "Backend is working"}
