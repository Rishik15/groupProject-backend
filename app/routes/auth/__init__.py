from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

from . import register
from . import login
from . import delete
from . import logout
from . import me
from . import googleOauth