from flask import Blueprint

# 1. Initialize the Blueprint for this folder
workouts_bp = Blueprint("workouts", __name__)

# 2. Import your route files at the bottom
# This ensures Flask registers the decorators (like @workoutLib_bp.route)
from . import predefinedPlans
from . import assignPlan