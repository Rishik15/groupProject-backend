from flask import Blueprint

notify_bp = Blueprint("notify", __name__)

from . import getNotifications
from . import readNotific
