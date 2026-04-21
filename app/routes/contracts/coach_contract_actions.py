from . import contract_bp
from flask import session, request, jsonify
import app.services.contracts.coachContractActions as cca


def _get_coach_id():
    c_id = session.get("user_id")
    if c_id is None:
        return None
    try:
        return int(c_id)
    except (TypeError, ValueError):
        return None


@contract_bp.route("/getAllCoachSideContracts", methods=["GET"])
def getAllCoachSideContracts():
    c_id = _get_coach_id()
    if c_id is None:
        return (
            jsonify({"error": "unauthorized access: no coach credential provided"}),
            401,
        )

    contracts = cca.getCoachContractsService(c_id) or []

    for contract in contracts:
        user_rows = cca.getUsersPerContract(contract["user_id"])
        if user_rows:
            contract["first_name"] = user_rows[0]["first_name"]
            contract["last_name"] = user_rows[0]["last_name"]
        else:
            contract["first_name"] = None
            contract["last_name"] = None

    return jsonify({"Response": contracts}), 200


@contract_bp.route("/getCoachActiveContracts", methods=["GET"])
def getCoachActiveContractsRoute():
    c_id = _get_coach_id()
    if c_id is None:
        return (
            jsonify({"error": "unauthorized access: no coach credential provided"}),
            401,
        )

    active_contracts = cca.getCoachContractsByStatusService(c_id, 1) or []
    return jsonify({"Response": active_contracts}), 200


@contract_bp.route("/getCoachInactiveContracts", methods=["GET"])
def getCoachInactiveContractsRoute():
    c_id = _get_coach_id()
    if c_id is None:
        return (
            jsonify({"error": "unauthorized access: no coach credential provided"}),
            401,
        )

    inactive_contracts = cca.getCoachContractsByStatusService(c_id, 0) or []
    return jsonify({"Response": inactive_contracts}), 200


@contract_bp.route("/coachAcceptContract", methods=["PATCH"])
def coachAcceptContractRoute():
    c_id = _get_coach_id()
    if c_id is None:
        return (
            jsonify({"error": "unauthorized access: no coach credential provided"}),
            401,
        )

    data = request.get_json(silent=True) or {}
    contract_id = data.get("contract_id")

    if contract_id is None:
        return jsonify({"error": "no contract_id provided"}), 400

    contract = cca.getSingleCoachContractService(c_id, contract_id)
    if not contract:
        return jsonify({"error": "contract not found for this coach"}), 404

    if contract["active"] == 1:
        return jsonify({"error": "contract is already active"}), 400

    client_id = cca.getUserGivenContract(contract_id)

    cca.coachAcceptsContractService(
        contract_id=contract_id, coach_id=c_id, user_id=client_id
    )
    return jsonify({"message": f"successfully accepted contract: {contract_id}"}), 200


@contract_bp.route("/coachRejectContract", methods=["PATCH"])
@contract_bp.route("/coachRegjectContract", methods=["PATCH"])  # backward compatibility
def coachRejectContractRoute():
    c_id = _get_coach_id()
    if c_id is None:
        return (
            jsonify({"error": "unauthorized access: no coach credential provided"}),
            401,
        )

    data = request.get_json(silent=True) or {}
    contract_id = data.get("contract_id")

    if contract_id is None:
        return jsonify({"error": "no contract_id provided"}), 400

    contract = cca.getSingleCoachContractService(c_id, contract_id)
    if not contract:
        return jsonify({"error": "contract not found for this coach"}), 404

    if contract["active"] == 1:
        return jsonify({"error": "cannot reject an already active contract"}), 400

    cca.coachRejectsContractService(contract_id)
    return jsonify({"message": f"successfully rejected contract: {contract_id}"}), 200


@contract_bp.route("/coachTerminateContract", methods=["PATCH"])
def coachTerminateContractRoute():
    c_id = _get_coach_id()
    if c_id is None:
        return (
            jsonify({"error": "unauthorized access: no coach credential provided"}),
            401,
        )

    data = request.get_json(silent=True) or {}
    contract_id = data.get("contract_id")

    if contract_id is None:
        return jsonify({"error": "no contract_id provided"}), 400

    contract = cca.getSingleCoachContractService(c_id, contract_id)
    if not contract:
        return jsonify({"error": "contract not found for this coach"}), 404

    if contract["active"] == 0:
        return jsonify({"error": "contract is already inactive"}), 400

    cca.coachTerminatesContractService(contract_id)
    return jsonify({"message": f"successfully terminated contract: {contract_id}"}), 200
