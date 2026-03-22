from flask import Blueprint

# 1. Initialize the Blueprint for this folder
coach_bp = Blueprint("coach", __name__)

from . import searchCoaches
from . import coachReview
