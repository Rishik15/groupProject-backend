from . import contract_bp
from flask import session, request, jsonify
from app.services.contracts.coachContractActions import getCoachContractsService
"""

For all contracts: 
need a list of all from the user_coach_contract: created_at, start_data, end_date, agreed_price, contract_text, from the connection with user_id: need the client name. 

I then need the count of pending and active contracts
then return the lists of contract objects where the active is pending, another where iti is pending, and the final one where it is inactive and active
need the accept contract endpoint, that updates the pending contract to make it active and sets the start date as the accepted date
need the decline contract endpoint
and also need a terminate contract endpoint, setting active to inactive


"""

@contract_bp("getAllCoachSideContracts", methods=[])
def getAllCoachSideContracts():

    results = []
    validResult = {}
    contracts = getCoachContractsService(c_id) if getCoachContractsService(c_id) is not None else None 
    for contract in contracts: 
        getUsersPerContract(contract.get("user_id"))

    
    return jsonify(validResult), 200

