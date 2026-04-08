from . import contract_bp
from flask import session, request, jsonify
import app.services.contracts.coachContractActions as cca
@contract_bp.route("/getAllCoachSideContracts", methods=["GET"])
def getAllCoachSideContracts():
    c_id = session.get("user_id")  
    if c_id is None: 
        return jsonify({"error": "unauthorized access:  no coach credential provided" }), 400
    c_id = int(c_id)
    
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
    c_id = session.get("user_id")  
    if c_id is None: 
        return jsonify({"error": "unauthorized access:  no coach credential provided" }), 400
    c_id = int(c_id)
    activeContracts = cca.getCoachActiveContractsService(c_id, 1) or []
    return jsonify({"Response":activeContracts}), 200

@contract_bp.route("/getCoachInactiveContracts", methods=["GET"])
def getCoachInactiveContractsRoute():
    c_id = session.get("user_id")  
    if c_id is None: 
        return jsonify({"error": "unauthorized access:  no coach credential provided" }), 400
    c_id = int(c_id)
    activeContracts = cca.getCoachActiveContractsService(c_id, 0) or []
    return jsonify({"Response":activeContracts}), 200

@contract_bp.route("/coachAcceptContract", methods=["PATCH"])
def coachAcceptContractRoute():
    c_id = session.get("user_id")  
    if c_id is None: 
        return jsonify({"error": "unauthorized access:  no coach credential provided" }), 400
    c_id = int(c_id)


"""

For all contracts: 
need a list of all from the user_coach_contract: created_at, start_data, end_date, agreed_price, contract_text, from the connection with user_id: need the client name. 

I then need the count of pending and active contracts
then return the lists of contract objects where the active is pending, another where iti is pending, and the final one where it is inactive and active
need the accept contract endpoint, that updates the pending contract to make it active and sets the start date as the accepted date
need the decline contract endpoint
and also need a terminate contract endpoint, setting active to inactive


"""
