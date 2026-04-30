from . import test_bp


@test_bp.route("/health")
def health():
    return {"status": "ok", "message": "Backend is working"}
