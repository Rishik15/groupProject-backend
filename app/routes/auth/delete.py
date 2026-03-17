from . import auth_bp   
from app.services.auth.deleteUser import delete_account_service
from flask import jsonify, session

@auth_bp.route("/delete", methods=["DELETE"])
def delete_user_account():
    u_id = session.get('user_id')

    try:
        # We call the logic from the service layer 
        delete_account_service(user_id=u_id)
        session.clear()
        return jsonify({"message": "Account deleted successfully"}), 200 
    except Exception as e:
        return jsonify({"error": str(e)}), 500 