from flask import Blueprint, request, jsonify, g, render_template, abort, session
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
  if not player:
    return abort(404)
  
  player_teams = get_player_teams(player_id)
  categories = get_rating_categories()
  average_ratings = get_player_avg_rating(player_id)
  
  user_email = "khaliun0122@gmail.com"#session.get("user_email", None)
  user_rating_dict = {}
  if user_email is not None:
    user_rating = get_user_rating(user_email, player_id)
    user_rating_dict = {rating[0]: rating[1] for rating in user_rating}
    
  categories_with_ratings = [
    {
      "category_id": category_id, 
      "category_name": category_name, 
      "average_rating": average_ratings.get(category_id, 0),
      "user_rating": user_rating_dict.get(category_id, None)
    }
    for category_id, category_name in categories
  ]
  
  if categories_with_ratings:
      overall_rating = round(sum(c["average_rating"] for c in categories_with_ratings) / len(categories_with_ratings), 1)
  else:
      overall_rating = 0 
      
  return render_template(
    Routes.PUBLIC_PLAYER_DETAIL.template, 
    player=player, 
    teams=player_teams, 
    categories=categories_with_ratings,
    overall_rating=overall_rating,
    has_user_ratings=(len(user_rating_dict) > 0)
  )
