from . import contract_bp
from flask import session, request, jsonify
import app.services.contracts.coachContractActions as cca


def _get_coach_id():
    coach_id = session.get("user_id")

    if coach_id is None:
        return None

    try:
        return int(coach_id)
    except (TypeError, ValueError):
        return None


def _get_session_timezone():
    return session.get("timezone") or "America/New_York"


@contract_bp.route("/getAllCoachSideContracts", methods=["GET"])
def getAllCoachSideContracts():
    """
    Get all coach contracts
    ---
    tags:
      - contracts
    responses:
      200:
        description: List of contracts
      401:
        description: Unauthorized
    """
    coach_id = _get_coach_id()

    if coach_id is None:
        return (
            jsonify({"error": "unauthorized access: no coach credential provided"}),
            401,
        )

    contracts = (
        cca.getCoachContractsService(
            coach_id=coach_id,
            user_timezone=_get_session_timezone(),
        )
        or []
    )

    return jsonify({"Response": contracts}), 200


@contract_bp.route("/getCoachActiveContracts", methods=["GET"])
def getCoachActiveContractsRoute():
    """
    Get active coach contracts
    ---
    tags:
      - contracts
    responses:
      200:
        description: Active contracts
      401:
        description: Unauthorized
    """
    coach_id = _get_coach_id()

    if coach_id is None:
        return (
            jsonify({"error": "unauthorized access: no coach credential provided"}),
            401,
        )

    active_contracts = (
        cca.getCoachContractsByStatusService(
            coach_id=coach_id,
            active=1,
            user_timezone=_get_session_timezone(),
        )
        or []
    )

    return jsonify({"Response": active_contracts}), 200


@contract_bp.route("/getCoachInactiveContracts", methods=["GET"])
def getCoachInactiveContractsRoute():
    """
    Get inactive coach contracts
    ---
    tags:
      - contracts
    responses:
      200:
        description: Inactive contracts
      401:
        description: Unauthorized
    """
    coach_id = _get_coach_id()

    if coach_id is None:
        return (
            jsonify({"error": "unauthorized access: no coach credential provided"}),
            401,
        )

    inactive_contracts = (
        cca.getCoachContractsByStatusService(
            coach_id=coach_id,
            active=0,
            user_timezone=_get_session_timezone(),
        )
        or []
    )

    return jsonify({"Response": inactive_contracts}), 200


@contract_bp.route("/coachAcceptContract", methods=["PATCH"])
def coachAcceptContractRoute():
    """
    Accept contract
    ---
    tags:
      - contracts
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - contract_id
          properties:
            contract_id:
              type: integer
    responses:
      200:
        description: Contract accepted
      400:
        description: Invalid input
      401:
        description: Unauthorized
      404:
        description: Contract not found
    """
    coach_id = _get_coach_id()

    if coach_id is None:
        return (
            jsonify({"error": "unauthorized access: no coach credential provided"}),
            401,
        )

    data = request.get_json(silent=True) or {}
    contract_id = data.get("contract_id")

    if contract_id is None:
        return jsonify({"error": "no contract_id provided"}), 400

    contract = cca.getSingleCoachContractService(
        coach_id=coach_id,
        contract_id=int(contract_id),
        user_timezone=_get_session_timezone(),
    )

    if not contract:
        return jsonify({"error": "contract not found for this coach"}), 404

    if contract["active"] == 1:
        return jsonify({"error": "contract is already active"}), 400

    if contract.get("end_date"):
        return jsonify({"error": "contract request is already closed"}), 400

    client_id = int(contract["user_id"])

    cca.coachAcceptsContractService(
        contract_id=int(contract_id),
        coach_id=coach_id,
        user_id=client_id,
        user_timezone=_get_session_timezone(),
    )

    return jsonify({"message": f"successfully accepted contract: {contract_id}"}), 200


@contract_bp.route("/coachRejectContract", methods=["PATCH"])
@contract_bp.route("/coachRegjectContract", methods=["PATCH"])
def coachRejectContractRoute():
    """
    Reject contract
    ---
    tags:
      - contracts
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - contract_id
          properties:
            contract_id:
              type: integer
    responses:
      200:
        description: Contract rejected
      400:
        description: Invalid input
      401:
        description: Unauthorized
      404:
        description: Contract not found
    """
    coach_id = _get_coach_id()

    if coach_id is None:
        return (
            jsonify({"error": "unauthorized access: no coach credential provided"}),
            401,
        )

    data = request.get_json(silent=True) or {}
    contract_id = data.get("contract_id")

    if contract_id is None:
        return jsonify({"error": "no contract_id provided"}), 400

    contract = cca.getSingleCoachContractService(
        coach_id=coach_id,
        contract_id=int(contract_id),
        user_timezone=_get_session_timezone(),
    )

    if not contract:
        return jsonify({"error": "contract not found for this coach"}), 404

    if contract["active"] == 1:
        return jsonify({"error": "cannot reject an already active contract"}), 400

    if contract.get("end_date"):
        return jsonify({"error": "contract request is already closed"}), 400

    cca.coachRejectsContractService(
        contract_id=int(contract_id),
        user_timezone=_get_session_timezone(),
    )

    return jsonify({"message": f"successfully rejected contract: {contract_id}"}), 200


@contract_bp.route("/coachTerminateContract", methods=["PATCH"])
def coachTerminateContractRoute():
    """
    Terminate contract
    ---
    tags:
      - contracts
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - contract_id
          properties:
            contract_id:
              type: integer
    responses:
      200:
        description: Contract terminated
      400:
        description: Invalid input
      401:
        description: Unauthorized
      404:
        description: Contract not found
    """
    coach_id = _get_coach_id()

    if coach_id is None:
        return (
            jsonify({"error": "unauthorized access: no coach credential provided"}),
            401,
        )

    data = request.get_json(silent=True) or {}
    contract_id = data.get("contract_id")

    if contract_id is None:
        return jsonify({"error": "no contract_id provided"}), 400

    contract = cca.getSingleCoachContractService(
        coach_id=coach_id,
        contract_id=int(contract_id),
        user_timezone=_get_session_timezone(),
    )

    if not contract:
        return jsonify({"error": "contract not found for this coach"}), 404

    if contract["active"] == 0:
        return jsonify({"error": "contract is already inactive"}), 400

    cca.coachTerminatesContractService(
        contract_id=int(contract_id),
        user_timezone=_get_session_timezone(),
    )

    return jsonify({"message": f"successfully terminated contract: {contract_id}"}), 200
