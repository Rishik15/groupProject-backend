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
    """
Get prediction markets pending review
---
tags:
  - admin-predictions
responses:
  200:
    description: Review queue
  401:
    description: Unauthorized
  403:
    description: Forbidden
"""
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
    """
Approve prediction market
---
tags:
  - admin-predictions
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required: [market_id]
      properties:
        market_id:
          type: integer
        admin_action:
          type: string
responses:
  200:
    description: Market approved
  400:
    description: Missing market_id
  401:
    description: Unauthorized
"""
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
    """
Reject prediction market
---
tags:
  - admin-predictions
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required: [market_id]
      properties:
        market_id:
          type: integer
        admin_action:
          type: string
responses:
  200:
    description: Market rejected
"""
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
    """
Get pending settlements
---
tags:
  - admin-predictions
responses:
  200:
    description: Pending settlement markets
"""
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
    """
Settle prediction market
---
tags:
  - admin-predictions
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required: [market_id, result]
      properties:
        market_id:
          type: integer
        result:
          type: string
        admin_action:
          type: string
responses:
  200:
    description: Market settled
"""
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
    """
Get cancellation requests
---
tags:
  - admin-predictions
responses:
  200:
    description: Cancellation queue
"""
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
    """
Approve market cancellation
---
tags:
  - admin-predictions
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required: [market_id]
responses:
  200:
    description: Cancellation approved
"""
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
    """
Reject market cancellation
---
tags:
  - admin-predictions
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required: [market_id]
responses:
  200:
    description: Cancellation rejected
"""
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