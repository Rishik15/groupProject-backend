from flask import Blueprint

# 1. Initialize the Blueprint for this folder
client_bp = Blueprint("client", __name__)

# 2. Import your route files at the bottom
# This ensures Flask registers the decorators (like @client_bp.route)
from . import mentalSurvey
from . import getInfo
from . import checkSurvey
from . import updateProfile
from . import progressPhotos
from . import getCoaches
from . import reportCoach
from . import reports
from . import getPreviousCoaches
