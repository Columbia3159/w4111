from flask import g
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import hashlib
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")

DATABASEURI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"

engine = create_engine(DATABASEURI, pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800)

def connect_db():
  try:
    g.conn = engine.connect()
  except Exception as e:
    print("Database connection failed")
    print(e)
    g.conn = None

def close_db():
  try:
    if hasattr(g, 'conn'):
      g.conn.close()
  except Exception as e:
    print("Failed to close the database connection")
    print(e)

def create_user(email, name, password):
  password = hashlib.sha256(password.encode()).hexdigest()
  cmd = "INSERT INTO users (email, name, password) VALUES (:email, :name, :password)"
  result = g.conn.execute(text(cmd).params(email=email.lower(), name=name, password=password))
  g.conn.commit() 
  
def authenticate(email, password):
  hashed_password = hashlib.sha256(password.encode()).hexdigest()
  cmd = "SELECT * FROM users WHERE email = :email AND password = :password"
  result = g.conn.execute(text(cmd), {"email": email.lower(), "password": hashed_password})
  user = next(result, None)
  return user
    
def get_users():
  cursor = g.conn.execute(text("SELECT name FROM users"))
  names = []
  for result in cursor:
    names.append(result)  
  cursor.close()
  return names

def get_players(page=1, search_query=""):
  rows_per_page = 10
  offset = (page - 1) * rows_per_page

  base_query = "SELECT *, COUNT(*) OVER() AS total_count FROM player"
  where_clause = ""
  params = {'rows_per_page': rows_per_page, 'offset': offset}
    
  if search_query and len(search_query) > 0:
    where_clause = "WHERE LOWER(player_name) LIKE :search"
    params['search'] = f"%{search_query}%"
      
  query = text(f"""
    {base_query}
    {where_clause}
    ORDER BY player_id ASC
    LIMIT :rows_per_page OFFSET :offset
  """)

  cursor = g.conn.execute(query, params)
  players_list = []
  for result in cursor:
    players_list.append(convert_player(result))  
  cursor.close()
  return players_list, 0 if len(players_list) == 0 else players_list[0]['total_count']

def get_player(player_id):
  query = text("SELECT * FROM player WHERE player_id = :player_id")
  result = g.conn.execute(query, {"player_id": player_id})
  player = next(result, None)
  return player

def get_player_teams(player_id):
  query = text("""SELECT * FROM team 
    INNER JOIN team_player ON team.team_id = team_player.team_id 
    WHERE player_id = :player_id
  """)
  cursor = g.conn.execute(query, {"player_id": player_id})
  teams = []
  for result in cursor:
    teams.append(result)  
  cursor.close()
  return teams

def get_team_players():
  query = text("""
    SELECT team.*, player.player_id, player_name, player_image, espn_rank 
    FROM team INNER JOIN team_player ON team.team_id = team_player.team_id 
              INNER JOIN player ON team_player.player_id = player.player_id
  """)
  cursor = g.conn.execute(query)
  teams = []
  for result in cursor:
    teams.append(result)  
  cursor.close()
  return teams

def get_rating_categories():
  query = text("SELECT * FROM rating_category")
  cursor = g.conn.execute(query)
  categories = []
  for result in cursor:
    categories.append(result)  
  cursor.close()
  return categories

def get_player_avg_rating(player_id):
  ratings_query = text("""
    SELECT category_id, ROUND(AVG(score), 1) AS average_rating
    FROM user_rating
    WHERE player_id = :player_id
    GROUP BY category_id
  """)
  ratings = g.conn.execute(ratings_query, {"player_id": player_id}).fetchall()
  average_ratings = {row[0]: row[1] for row in ratings}
  return average_ratings

def save_category_score(user, player_id, category_id, value):
  insert_query = text("""
    INSERT INTO user_rating (email, player_id, category_id, score)
    VALUES (:email, :player_id, :category_id, :rating_value)
    ON CONFLICT (email, player_id, category_id)
    DO UPDATE SET score = EXCLUDED.score
  """)
  g.conn.execute(insert_query, {
    "email": user,
    "player_id": player_id,
    "category_id": int(category_id),
    "rating_value": int(value)
  })
  
def delete_score(email, player_id):
  delete_query = text("""
    DELETE FROM user_rating
    WHERE player_id = :player_id AND email = :email
  """)
  g.conn.execute(delete_query, {"player_id": player_id, "email": email})
  g.conn.commit()
  
def get_user_rating(email, player_id):
  user_ratings_query = text("""
    SELECT category_id, score
    FROM user_rating
    WHERE player_id = :player_id AND email = :email
  """)
  user_ratings = g.conn.execute(user_ratings_query, {"player_id": player_id, "email": email}).fetchall()
  return user_ratings
  
def convert_player(player):
  return {
    "player_id": player[0],
    "player_name": player[1],
    "player_image":player[2],
    "espn_rank": player[3],
    "description": player[4],
    "points": player[5],
    "assists": player[6],
    "rebounds": player[7],
    "steals": player[8],
    "blocks": player[9],
    "turn_overs": player[10],
    "fg_percentage": player[11],
    "fg_3p_percentage": player[12],
    "ft_percentage": player[13],
    "total_count": player[14],
  }
  
def get_comments(player_id):
  comments_query = text("""
    SELECT c.comment_id, c.email, c.text, c.date, r.parent_id,
      SUM(CASE WHEN ucl.isLike THEN 1 ELSE 0 END) AS likes,
      SUM(CASE WHEN NOT ucl.isLike THEN 1 ELSE 0 END) AS dislikes
    FROM comment c
    LEFT JOIN user_comment_like ucl ON c.comment_id = ucl.comment_id
    LEFT JOIN reply r ON c.comment_id = r.child_id
    WHERE c.player_id = :player_id
    GROUP BY c.comment_id, r.parent_id
    ORDER BY c.date DESC
  """)
  comments = g.conn.execute(comments_query, {"player_id": player_id}).fetchall()
  return comments

def save_comment(player_id, user_email, comment):
  insert_comment_query = text("""
    INSERT INTO comment (player_id, email, text)
    VALUES (:player_id, :email, :text)
    RETURNING comment_id
  """)
  result = g.conn.execute(insert_comment_query, {
    "player_id": player_id,
    "email": user_email,
    "text": comment
  })
  new_comment_id = result.scalar()
  return new_comment_id
  
def save_reply(parent_id, child_id):
  reply_query = text("""
    INSERT INTO Reply (parent_id, child_id)
    VALUES (:parent_id, :child_id)
  """)
  g.conn.execute(reply_query, {"parent_id": parent_id, "child_id": child_id})
  
def user_like_comment(user_email, comment_id):
  query = text("""
    INSERT INTO user_comment_like (email, comment_id, isLike)
    VALUES (:email, :comment_id, TRUE)
    ON CONFLICT (email, comment_id)
    DO UPDATE SET isLike = TRUE
  """)
  g.conn.execute(query, {"email": user_email, "comment_id": comment_id})
  g.conn.commit()
  

def user_dislike_comment(user_email, comment_id):
  query = text("""
    INSERT INTO user_comment_like (email, comment_id, isLike)
    VALUES (:email, :comment_id, FALSE)
    ON CONFLICT (email, comment_id)
    DO UPDATE SET isLike = FALSE
  """)
  g.conn.execute(query, {"email": user_email, "comment_id": comment_id})
  g.conn.commit()