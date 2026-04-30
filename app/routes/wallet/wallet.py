# app/routes/wallet/wallet.py
from flask import Blueprint, jsonify, session
from app.services.wallet.wallet import (
    get_wallet,
    get_wallet_transactions,
)

wallet_bp = Blueprint("wallet", __name__)


@wallet_bp.route("", methods=["GET"])
def get_wallet_route():
    """
Get user wallet
---
tags:
  - wallet
responses:
  200:
    description: Wallet data
    schema:
      type: object
      properties:
        message:
          type: string
        wallet:
          type: object
          properties:
            user_id:
              type: integer
            balance:
              type: integer
            created_at:
              type: string
            updated_at:
              type: string
  401:
    description: Unauthorized
"""
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
    """
Get wallet transactions
---
tags:
  - wallet
responses:
  200:
    description: List of wallet transactions
    schema:
      type: object
      properties:
        message:
          type: string
        transactions:
          type: array
          items:
            type: object
            properties:
              txn_id:
                type: integer
              user_id:
                type: integer
              delta_points:
                type: integer
              reason:
                type: string
              ref_type:
                type: string
              ref_id:
                type: integer
              created_at:
                type: string
              updated_at:
                type: string
  401:
    description: Unauthorized
"""
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