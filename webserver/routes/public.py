from flask import Blueprint, request, jsonify, g, render_template, abort
from sqlalchemy import text
from app_routes import Routes
from db import *

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
  return render_template(Routes.PUBLIC_HOME.template)

@public_bp.route('/player/<int:player_id>')
def player(player_id):
  player = get_player(player_id)
  player_teams = get_player_teams(player_id)
  if not player:
    return abort(404)
  return render_template(Routes.PUBLIC_PLAYER_DETAIL.template, player=player, teams=player_teams)
