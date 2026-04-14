from flask import Blueprint

# 1. Initialize the Blueprint for this folder
exercise_bp = Blueprint("exercise", __name__)

# 2. Import your route files at the bottom
# This ensures Flask registers the decorators (like @client_bp.route)
from . import searchExercises
