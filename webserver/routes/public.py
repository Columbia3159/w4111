from flask import Blueprint, request, jsonify, g, render_template, abort, session
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
  
  user_email = session.get("user_email", None)
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
      
  comments = get_player_comments(player_id)
      
  return render_template(
    Routes.PUBLIC_PLAYER_DETAIL.template, 
    player=player, 
    teams=player_teams, 
    categories=categories_with_ratings,
    overall_rating=overall_rating,
    has_user_ratings=(len(user_rating_dict) > 0),
    comments=comments
  )
  
@public_bp.route('/compare/<int:player_id>')
def compare(player_id):
  return render_template(
    Routes.PUBLIC_PLAYER_COMPARE.template, 
    player1_id=player_id,
  )

def get_player_comments(player_id):
  comments_with_replies = get_comments(player_id)
  comments = {}
  
  for row in comments_with_replies:
    comment = {
      "id": row[0],
      "email": row[1],
      "text": row[2],
      "date": row[3],
      "likes": row[5],
      "dislikes": row[6],
      "replies": []
    }
    comments[row[0]] = comment
    
  organized_comments = [] 
  for row in comments_with_replies:
    parent_id = row[4]
    if parent_id is None: 
      organized_comments.append(comments[row[0]])
    else: 
      parent = comments.get(parent_id)
      if parent:
        parent["replies"].append(comments[row[0]])
      else:
        print(f"Warning: Parent comment ID {parent_id} not found for reply ID {row[0]}")
  return organized_comments
