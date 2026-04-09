from flask import Blueprint

# 1. Initialize the Blueprint for this folder
coach_bp = Blueprint("coach", __name__)

from . import searchCoaches
from . import updateCoach
from . import updateCerts
from . import updateAvailability
from . import coachReview
from . import getCoachProfile