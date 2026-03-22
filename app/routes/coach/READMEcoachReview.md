- localhost:8080/coach/get_review
- localhost:8080/coach/leave_review

## send in session :

- user_id

# get coaches reviews
in json via axios provide 

- target coach_id (for get)

## expect : 

```json

{
"coach_avg_rating" : float
"reviews" : [ {"review_id": int, "rating": int, "review_text": str, "reviewer_first_name": str, "reviewer_last_name" : str, "created_at": datetime(isoFormat), "updated_at": datetime(isoFormat)} ] (list of dictionaries)
"coach_first_name" : str
"coach_last_name": str
}

```

as a json object of course
I will also make a readme for this
please read above carefully it is not what you originally sent
I added more implied information based on the table cols 


if the coach id does not exist we raise a "coach not found" value error 

otherwise you will recieve the expected json

# leaving review

you must provide (through the json via axios) : 

data=```json

"coach_id" : int
"rating" : int (1-5) must be an int
"review_text": str

```