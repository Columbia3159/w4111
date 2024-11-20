from flask import Blueprint, request, jsonify, g, render_template, session
from sqlalchemy import text
from app_routes import Routes
from db import *

api_bp = Blueprint('api', __name__)

@api_bp.route('/players', methods=['GET'])
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