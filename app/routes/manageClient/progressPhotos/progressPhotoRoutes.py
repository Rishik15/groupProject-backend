from flask import jsonify, request, session

from app.routes.manageClient.progressPhotos import manage_progress_photos_bp
from app.utils.Contract.getClientId import getClientIdFromContract
from app.services.client.progress_photos import get_progress_photos


def _get_session_timezone():
    return session.get("timezone") or "America/New_York"


def get_client_id_from_contract():
    coach_id = session.get("user_id")

    if not coach_id:
        return None, (jsonify({"error": "Unauthorized"}), 401)

    contract_id = request.args.get("contract_id", type=int)

    if not contract_id:
        return None, (jsonify({"error": "contract_id is required"}), 400)

    client_id = getClientIdFromContract(contract_id, coach_id)

    if not client_id:
        return None, (jsonify({"error": "Invalid contract or access denied"}), 404)

    return int(client_id), None


@manage_progress_photos_bp.route("/progress-photos", methods=["GET"])
def manage_client_progress_photos_route():
    client_id, error = get_client_id_from_contract()

    if error:
        return error

    try:
        photos = get_progress_photos(
            user_id=client_id,
            user_timezone=_get_session_timezone(),
        )

        return (
            jsonify(
                {
                    "message": "success",
                    "progressPhotos": photos if photos is not None else [],
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
