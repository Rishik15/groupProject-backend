from flask import Blueprint

nutrition_bp = Blueprint("nutrition", __name__)

from . import logMeals
from . import getMealPlans
from . import getMealPlanDetails
from . import assignMealPlan
from . import createFoodItem
from . import getMeals
from . import createMealPlan