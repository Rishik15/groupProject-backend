from flask import Blueprint

manage_nutrition_bp = Blueprint("manage_nutrition", __name__)

from . import nutritionRoutes
from . import mealPlan
