from flask import Blueprint

dashboard_client_bp = Blueprint("dashClient", __name__)

from . import getNutrition
from . import dailyMetrics
from . import getWeight
from . import getWorkouts
from . import getCalories