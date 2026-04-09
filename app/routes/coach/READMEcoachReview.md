## Coach Review Endpoints

### Routes

- localhost:8080/coach/get_review  
- localhost:8080/coach/leave_review  
- localhost:8080/coach/get_coach_info

---

## Session Requirements

The following value must exist in the session:

- user_id  

---

## Get Coach Reviews

### Request

Send the target coach_id in JSON via Axios.

### Example Request Body

```json
{
  "coach_id": 12
}
```

### Behavior

- If the provided coach id does not exist, a "coach not found" ValueError is raised.
- Otherwise, the endpoint returns the expected JSON object containing the coach's review summary and review list.

### Response Format

```json
{
  "coach_avg_rating": 4.75,
  "reviews": [
    {
      "review_id": 3,
      "rating": 5,
      "review_text": "Great coach, very helpful.",
      "reviewer_first_name": "John",
      "reviewer_last_name": "Doe",
      "created_at": "2026-03-22T14:30:00",
      "updated_at": "2026-03-22T14:30:00"
    }
  ],
  "coach_first_name": "Jane",
  "coach_last_name": "Smith"
}
```

### Response Fields

- coach_avg_rating : float  
- reviews : list of review objects  
  - review_id : int  
  - rating : int  
  - review_text : str  
  - reviewer_first_name : str  
  - reviewer_last_name : str  
  - created_at : datetime (ISO format string)  
  - updated_at : datetime (ISO format string)  
- coach_first_name : str  
- coach_last_name : str  

---

## Leave Review

### Request

You must provide the following fields in JSON via Axios:

```json
{
  "coach_id": 12,
  "rating": 5,
  "review_text": "Very knowledgeable and easy to work with."
}
```

### Required Fields

- coach_id : int  
- rating : int (must satisfy 1 <= rating <= 5)  
- review_text : str  

---

## Validation Rules

- rating must be an integer  
- rating must be between 1 and 5  
- user must be authenticated (session must contain user_id)  
- user must be a client  
- user must have worked with the coach (user_coach_contract)  
- user may only leave one review per coach  

---

## Success Response

```json
{
  "message": "success"
}
```

---

## Error Cases

- 401 Unauthorized → missing session  
- 400 Bad Request → invalid or missing input  
- 403 Forbidden → user not allowed to review coach  
- 404 Not Found → coach does not exist ("coach not found")  
- 409 Conflict → user already reviewed this coach  
- 500 Internal Server Error → unexpected failure  

# later addition get coach information : 


```json
    Response:
    {
        "first_name": str,
        "last_name": str,
        "price": number,
        "coach_description": str,
        "profile_picture": str,
        "weight": number,
        "height": number
    }
```