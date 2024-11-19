from flask import Blueprint, request, jsonify, g, render_template
from sqlalchemy import text
from app_routes import Routes
from db import *

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
  names = get_users()
  context = dict(data = names)
  return render_template(Routes.PUBLIC_HOME.template, **context)