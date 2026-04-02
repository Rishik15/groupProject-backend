


# localhost:8080/nutrition/getFoodItems 

- returns a json of all the previous user entries (in the frontend this should display as a dropdown with an other option that lets the user create a food item )


```json
{
"message": str,
"foodItemsList" : (list(dicts)) example of this below
    [
        {food_item_id,
        name,
        calories, 
        protein,
        carbs,
        fats,
        image_url} 
        ... 
    ]  
}
``` 
and status code 200

# localhost:8080/nutrition/createFoodItem
 
takes in 

```json
{
"name": str ,
"calories": int, 
"protein": int ,
"carbs":  int  ,
"fats":  int,
"image_url" : str (URL format)  -  use a default image if the user doesnt add one
}
```

all fields are treated as required

you may then getFoodItems to see the update 

# localhost:8080/nutrition/logMeal

Logs a meal for the currently authenticated user.

The backend will:
- validate the authenticated session
- validate request body fields
- parse `eaten_at` using datetime.fromisoformat(...)
- fetch all provided food_item_ids for the user
- sum calories/macros across those food items
- create a new row in `meal`
- create a new row in `meal_log` referencing that meal

## Method

POST

## Auth

Requires session:

- session["user_id"]

If missing:

```json
{
  "error": "Unauthorized"
}
```

Status: 401

## Request Body

```json
{
  "name": "str",
  "eaten_at": "datetime (ISO format)",
  "servings": "int",
  "notes": "str (optional)",
  "photo_url": "str (URL)",
  "food_item_ids": ["list[int]"]
}
```

## Required Fields

- name: str
- eaten_at: datetime (ISO format, parsed using datetime.fromisoformat)
- servings: int
- photo_url: str
- food_item_ids: list[int] (must contain at least one id)

## Optional Fields

- notes: str

## Field Notes

- eaten_at
  - must be ISO format
  - backend uses datetime.fromisoformat(...)
  - stored and returned as .isoformat()

- food_item_ids
  - must all belong to the authenticated user
  - backend fetches and aggregates their macros

## Success Response

```json
{
  "message": "success"
}
```

Status: 200

## Error Cases

### Missing Fields

```json
{
  "error": "one of the required fields was not provided"
}
```

Status: 400

### Invalid food_item_ids

```json
{
  "error": "food_item_ids must be a non-empty list"
}
```

Status: 400

### Invalid Datetime

```json
{
  "error": "eaten_at must be a valid ISO datetime string"
}
```

Status: 400

### Invalid Ownership / Nonexistent Items

```json
{
  "error": "one or more food items do not exist for this user"
}
```

Status: 400



# localhost:8080/nutrition/getLoggedMeals

Returns logged meals for the currently authenticated user.

This endpoint returns rows from `meal_log` joined with `meal`.

All datetime fields are:
- parsed from DB into datetime objects
- returned using .isoformat()

## Method

POST

## Auth

Requires session:

- session["user_id"]

If missing:

```json
{
  "error": "Unauthorized"
}
```

Status: 401

## Request Body

```json
{
  "start_datetime": "datetime (ISO format, optional)",
  "end_datetime": "datetime (ISO format, optional)"
}
```

## Optional Fields

- start_datetime: datetime (ISO format)
- end_datetime: datetime (ISO format)

## Filter Behavior

- if start_datetime provided:
  - meal_log.eaten_at >= start_datetime

- if end_datetime provided:
  - meal_log.eaten_at <= end_datetime

- if neither provided:
  - return all meals

- both values parsed using datetime.fromisoformat(...)

## Success Response

```json
{
  "message": "success",
  "loggedMeals": [
    {
      "log_id": "int",
      "user_id": "int",
      "meal_id": "int",
      "food_item_id": "int | null",
      "eaten_at": "datetime (ISO format)",
      "servings": "int",
      "notes": "str | null",
      "photo_url": "str",
      "created_at": "datetime (ISO format)",
      "updated_at": "datetime (ISO format)",
      "meal_name": "str",
      "calories": "int",
      "protein": "float",
      "carbs": "float",
      "fats": "float"
    }
  ]
}
```

Status: 200

## Error Cases

### Invalid Datetime Filters

```json
{
  "error": "start_datetime and end_datetime must be valid ISO datetime strings"
}
```

Status: 400

### Unauthorized

```json
{
  "error": "Unauthorized"
}
```

Status: 401
__________________________________________________________________
Log meal has the following fields : 

meal type 
meal name 
photo 
calories 
protein 
carbs
fat

what we will do : 
allow user to add images of the full meal 
pull in items from a database / insert their own items with information 
sum up the components (food_items) of the meal and add that into meal log and create a meal instance that can be stored in meals and displayed in meal history (we will not be working with meal_plans directly )
i.e. : calories of meal = for f in food_items : tot_calories += f.get(calories)

meal table actually takes 

name : str
calories: int 
protein : int
carbs : int
fats : int 

meal_log table takes

eaten_at : datetimeisoformat
servings : int 
notes: str
photo_url : str (url) 

food_item table takes  (either from user or from database)

name : str 
calories: int
protein : int
carbs: int
fats: int 
image_url: str(url)


All of the following fields are required from the frontend 
you can populate unchanged entries in the json object using the current value of the 
food item

data = 

```json 
{ 
"food_id": int   ,//(default = /getFoodItems @ "food_id")       
"name": str      ,//(default = /getFoodItems @ "name")   
"calories": int  ,//(default = /getFoodItems @ "calories")           
"protein": int   ,//(default = /getFoodItems @ "protein")       
"carbs": int     ,//(default = /getFoodItems @ "carbs")       
"fats": int      ,//(default = /getFoodItems @ "fats")           
"image_url": str ,//(default = /getFoodItems @ "image_url")       

}  ```       


localhost:8080/nutrition/updateFoodItem