from flask import Blueprint

onboard_bp = Blueprint("onboard", __name__)

from . import onboard
from . import coachApplication
