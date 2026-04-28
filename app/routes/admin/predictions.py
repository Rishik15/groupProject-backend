from flask import jsonify, request, session
from . import admin_bp
from app.services.predictions.markets import (
    get_admin_prediction_review_queue,
    approve_prediction_market,
    reject_prediction_market,
    get_admin_pending_settlement_queue,
    settle_prediction_market,
    get_admin_prediction_cancel_review_queue,
    approve_prediction_market_cancellation,
    reject_prediction_market_cancellation,
)


@admin_bp.route("/predictions/review", methods=["GET"])
def admin_get_prediction_review_queue():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        markets = get_admin_prediction_review_queue(int(user_id))

        return jsonify({
            "message": "success",
            "markets": markets
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/predictions/approve", methods=["PATCH"])
def admin_approve_prediction_market():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        market_id = data.get("market_id")
        admin_action = data.get("admin_action")

        if not market_id:
            return jsonify({"error": "market_id is required"}), 400

        market = approve_prediction_market(
            admin_user_id=int(user_id),
            market_id=market_id,
            admin_action=admin_action
        )

        return jsonify({
            "message": "success",
            "market": market
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/predictions/reject", methods=["PATCH"])
def admin_reject_prediction_market():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        market_id = data.get("market_id")
        admin_action = data.get("admin_action")

        if not market_id:
            return jsonify({"error": "market_id is required"}), 400

        market = reject_prediction_market(
            admin_user_id=int(user_id),
            market_id=market_id,
            admin_action=admin_action
        )

        return jsonify({
            "message": "success",
            "market": market
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/predictions/pending-settlement", methods=["GET"])
def admin_get_pending_settlement_queue():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        markets = get_admin_pending_settlement_queue(int(user_id))

        return jsonify({
            "message": "success",
            "markets": markets
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/predictions/settle", methods=["PATCH"])
def admin_settle_prediction_market():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        market_id = data.get("market_id")
        result = data.get("result")
        admin_action = data.get("admin_action")

        if not market_id:
            return jsonify({"error": "market_id is required"}), 400

        if not result:
            return jsonify({"error": "result is required"}), 400

        market = settle_prediction_market(
            admin_user_id=int(user_id),
            market_id=market_id,
            result=result,
            admin_action=admin_action
        )

        return jsonify({
            "message": "success",
            "market": market,
            "result": {
                "result": market["result"]
            }
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/predictions/cancel-review", methods=["GET"])
def admin_get_prediction_cancel_review_queue():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        markets = get_admin_prediction_cancel_review_queue(int(user_id))

        return jsonify({
            "message": "success",
            "requests": markets
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/predictions/approve-cancel", methods=["PATCH"])
def admin_approve_prediction_market_cancellation():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        market_id = data.get("market_id")
        admin_action = data.get("admin_action")

        if not market_id:
            return jsonify({"error": "market_id is required"}), 400

        market = approve_prediction_market_cancellation(
            admin_user_id=int(user_id),
            market_id=market_id,
            admin_action=admin_action
        )

        return jsonify({
            "message": "success",
            "market": market
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/predictions/reject-cancel", methods=["PATCH"])
def admin_reject_prediction_market_cancellation():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        market_id = data.get("market_id")
        admin_action = data.get("admin_action")

        if not market_id:
            return jsonify({"error": "market_id is required"}), 400

        market = reject_prediction_market_cancellation(
            admin_user_id=int(user_id),
            market_id=market_id,
            admin_action=admin_action
        )

        return jsonify({
            "message": "success",
            "request": {
                "market_id": market["market_id"],
                "status": market["cancel_request_status"]
            },
            "market": market
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500