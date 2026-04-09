- endpoint : /contract/getAllCoachSideContracts

method = GET

based on the current user_id from the session (i.e. the coach_id I will return all active contracts as follows)

returns 

```json 
{
    "Response": 
    [
        {
        "user_id": int,
        "active": int in range(0,1)
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

OR 

{
    "error": ...
}

```


- endpoint contract/getCoachActiveContracts // active = 1
- endpoint contract/getCoachInactiveContracts // active = 0


expects valid coach id 

returns 

```json
{
    "Response": [
        "user_id": int,
        "active": int in range(0,1)
        "contract_id" : int, 
        "created_at": datetime obj  , //iso format 
        "start_date": datetime obj  , //iso format  
        "end_date":    datetime obj  , //iso format 
        "agreed_price": number ,
        "contract_text": str,
        "created_at": datetime obj , //iso format 
        "updated_at": datetime obj , //iso format 

    ]

}

OR 

{
    "error": ...
}


```

- endpoint contract/coachAcceptContract 

### **IMPORTANT** 
- ### endpoint is expecting **contract_id** && **active** in the data dict / json object 

active must be 0 for you to be able to run this endpoint

This endpoint will set active = 1 (true) for that contract_id and will set the start_date to datetime.now().isoformat()

returns 

```json

{
    "message": "success"
}
 
OR 

{
    "error": ...
}
```


- endpoint contract/coachRegjectContract 

### **IMPORTANT** 
- ### endpoint is expecting **contract_id** && **active** in the data dict / json object 


active must be 0 for you to be able to run this endpoint

This endpoint will set active to 0 ( assuming it is already 0) for that contract_id and will set the end_date to datetime.now().isoformat()

returns 

```json

{
    "message": "success"
}
 
OR 

{
    "error": ...
}
```

- endpoint contract/coachTerminateContract 

### **IMPORTANT** 
- ### endpoint is expecting **contract_id**  in the data dict / json object 


active must be 0 for you to be able to run this endpoint

This endpoint will set active to 0 ( assuming it is already 0) for that contract_id and will set the end_date to datetime.now().isoformat()

returns 

```json

{
    "message": "success"
}
 
OR 

{
    "error": ...
}
```

