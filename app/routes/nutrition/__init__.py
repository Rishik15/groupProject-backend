from flask import Blueprint

nutrition_bp = Blueprint("nutrition", __name__)

from . import logMeals
from . import getNutritionToday
from . import getMealPlans
from . import getMealPlanDetails
from . import assignMealPlan
from . import createFoodItem
from . import getMeals
from . import createMealPlan
from . import updateMealPlan
from . import getMyMealPlans
from . import deleteMealPlan
from . import getTodaysMeals
from . import logMealFromPlan
from . import getWeeklyCalories
from . import getWeeklyCaloriesSummary
from . import logFoodItem
