from flask import Blueprint

predictions_bp = Blueprint("predictions", __name__)

from . import markets
from . import bets