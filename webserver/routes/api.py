from flask import Blueprint, request, jsonify, g, render_template, session
from app_routes import Routes
from db import *

api_bp = Blueprint('api', __name__)

@api_bp.route('/players', methods=['GET'])
def player_list():
  page = int(request.args.get('page', 1))  
  rows_per_page = int(request.args.get('rows_per_page', 10))  
  search_query = request.args.get('search', '').strip().lower()
  players_list, total_rows = get_players(page, rows_per_page, search_query)
  return jsonify({
    "players": players_list,
    "total_rows": total_rows,
    "rows_per_page": rows_per_page,
    "current_page": page
  })
  
@api_bp.route('/rating', methods=['POST'])
def submit_rating():
  try:
    data = request.get_json()
    player_id = data.get('player_id')
    ratings = data.get('ratings') 
    user = session.get("user_email", None)
    
    if user is None:
      return {"error": "User not logged in"}, 401
    if not player_id or not ratings:
      return {"error": "Invalid input"}, 400

    for category_id, value in ratings.items():
      save_category_score(user, player_id, category_id, value)
      
    g.conn.commit()

    return {"message": "Ratings saved successfully"}, 200
  except Exception as e:
    return {"error": "An error occurred while saving ratings"}, 500
  
@api_bp.route('/rating/<int:player_id>', methods=['DELETE'])
def delete_rating(player_id):
  try:
    user = session.get("user_email", None)
    if not user:
        return {"error": "User not logged in"}, 401
    delete_score(user, player_id)
    return {"message": "Ratings deleted successfully"}, 200
  except Exception as e:
    print(e)
    return {"error": "An error occurred while deleting ratings"}, 500
  
@api_bp.route('/comment', methods=['POST'])
def submit_comment():
  try:
    data = request.get_json()
    player_id = data.get('player_id')
    comment = data.get('comment') 
    user = session.get("user_email", None)
    
    if user is None:
      return {"error": "User not logged in"}, 401

    save_comment(player_id, user, comment)
    g.conn.commit()

    return {"message": "Comment saved successfully"}, 200
  except Exception as e:
    return {"error": "An error occurred while saving comment"}, 500
  
@api_bp.route('/comment/like/<int:comment_id>', methods=['POST'])
def like_comment(comment_id):
  user_email = session.get("user_email", None)
  if not user_email:
    return {"error": "User not logged in."}, 401
  try:
    user_like_comment(user_email, comment_id)
    return {"message": "Liked successfully."}, 200
  except Exception as e:
    print(e)
    return {"error": "An error occurred while processing your request."}, 500

@api_bp.route('/comment/dislike/<int:comment_id>', methods=['POST'])
def dislike_comment(comment_id):
  user_email = session.get("user_email", None)
  if not user_email:
    return {"error": "User not logged in."}, 401
  try:
    user_dislike_comment(user_email, comment_id)
    return {"message": "Disliked successfully."}, 200
  except Exception as e:
    print(e)
    return {"error": "An error occurred while processing your request."}, 500
  
@api_bp.route('/comment/reply', methods=['POST'])
def add_reply():
  data = request.get_json()
  parent_id = data.get('parent_id')
  player_id = data.get('player_id')
  reply_text = data.get('reply')
  user_email = session.get("user_email", None)

  if not parent_id or not reply_text or not user_email:
    return {"error": "Invalid input."}, 400

  try:
    new_comment_id = save_comment(player_id, user_email, reply_text)
    save_reply(parent_id, new_comment_id)
    g.conn.commit()

    return {"message": "Reply added successfully."}, 200
  except Exception as e:
    print(e)
    return {"error": "An error occurred while adding the reply."}, 500

@api_bp.route('/player/<int:player_id>', methods=['GET'])
def get_player(player_id):
  categories = get_rating_categories()
  results = get_player_avg_rating_detail(player_id)
  
  if not results:
    return {"error": "Player not found"}, 404

  player_data = {
    "player_id": results[0][0],
    "player_name": results[0][1],
    "ratings": {row[3]: row[4] for row in results},
    "categories": dict(categories)
  }
  
  return player_data
