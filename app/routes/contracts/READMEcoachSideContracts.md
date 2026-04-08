endpoint : localhost8080/contract/getAllCoachSideContracts

method = GET

based on the current user_id from the session (i.e. the coach_id I will return all active contracts as follows)

returns 

```json 
{
    "repsonseList": 
    [
        {
        "contract_id" : int, 
        "created_at": datetime obj  , //iso format 
        "start_date": datetime obj  , //iso format , 
        "end_date":    datetime obj  , //iso format ,
        "agreed_price": number ,
        "contract_text": str,
        "first_name": str, // clients name
        "last_name": str// clients name
        }
    ]
}

```