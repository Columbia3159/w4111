from flask import Blueprint, request, jsonify, g, render_template, abort
from sqlalchemy import text
from app_routes import Routes
from db import *

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
  team_players = get_team_players()
  teams = {}
  for row in team_players:
    team_id = row[0]
    if team_id not in teams:
      teams[team_id] = {
        "team_name": row[1],
        "team_image": row[2],
        "players": []
      }
    teams[team_id]["players"].append({
      "player_id": row[3],
      "player_name": row[4],
      "player_image": row[5],
      "espn_rank": row[6],
    })
  return render_template(Routes.PUBLIC_HOME.template, teams=teams)

@public_bp.route('/player/<int:player_id>')
def player(player_id):
  player = get_player(player_id)
  player_teams = get_player_teams(player_id)
  if not player:
    return abort(404)
  return render_template(Routes.PUBLIC_PLAYER_DETAIL.template, player=player, teams=player_teams)
