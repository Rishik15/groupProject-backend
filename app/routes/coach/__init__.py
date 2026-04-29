from flask import Blueprint

# 1. Initialize the Blueprint for this folder
coach_bp = Blueprint("coach", __name__)

from . import searchCoaches
from . import updateCoach
from . import updateCerts
from . import addCerts
from . import updateAvailability
from . import coachReview
from . import getClients
from . import assignClientPlan
from . import getCoachProfile
from . import createExercises
from . import myExercises
from . import deleteCerts
from . import activateCoachMode
from . import price_updates
