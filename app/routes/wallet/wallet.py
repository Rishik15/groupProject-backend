# app/routes/wallet/wallet.py
from flask import Blueprint, jsonify, session
from app.services.wallet.wallet import (
    get_wallet,
    get_wallet_transactions,
)

wallet_bp = Blueprint("wallet", __name__)


@wallet_bp.route("", methods=["GET"])
def get_wallet_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        wallet = get_wallet(int(user_id))

        return jsonify({
            "message": "success",
            "wallet": wallet
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@wallet_bp.route("/transactions", methods=["GET"])
def get_wallet_transactions_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        transactions = get_wallet_transactions(int(user_id))

        return jsonify({
            "message": "success",
            "transactions": transactions
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500