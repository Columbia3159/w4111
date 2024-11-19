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

@public_bp.route('/api/players', methods=['GET'])
def player_list():
  page = int(request.args.get('page', 1))  
  search_query = request.args.get('search', '').strip().lower()
  players_list, total_rows = get_players(page, search_query)
  return jsonify({
    "players": players_list,
    "total_rows": total_rows,
    "rows_per_page": 10,
    "current_page": page
  })