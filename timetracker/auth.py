from flask import Blueprint
from .models import User


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    pass