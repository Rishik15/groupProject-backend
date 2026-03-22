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
