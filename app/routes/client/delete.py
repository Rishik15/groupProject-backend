# app/routes/client/delete.py
from . import client_bp 
from app.services.client.accountService import delete_account_service
from flask import jsonify

@client_bp.route("/delete/<int:user_id>", methods=["DELETE"])
def delete_user_account(user_id):
    try:
        # We call the logic from the service layer 
        result = delete_account_service(user_id=user_id)
        return jsonify({"message": "Success"}), 200 
    except Exception as e:
        return {"error": str(e)}, 500 