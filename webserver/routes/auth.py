from flask import Blueprint, request, jsonify, g, render_template, flash, redirect, url_for, abort, session
from app_routes import Routes
from db import *

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=Routes.AUTH_LOGIN.methods)
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    try:
      user = authenticate(email, password)
      if user:
        session['user_email'] = user[0]
        session['user_name'] = user[1]
        return redirect(url_for(Routes.PUBLIC_HOME.route))  
      else:
        common_error("User not found")
    except Exception as e:
      print(e)
      common_error()
      
    return render_template(Routes.AUTH_LOGIN.template, email=email)
  
  return render_template(Routes.AUTH_LOGIN.template)


@auth_bp.route('/signup', methods=Routes.AUTH_SIGNUP.methods)
def signup():
  if request.method == 'POST':
    try:
      name = request.form['name']
      email = request.form['email']
      password = request.form['password']
      
      create_user(email, name, password)
      user = authenticate(email, password)
      if user:
        session['user_email'] = user[0]
        session['user_name'] = user[1]
        return(redirect(url_for(Routes.PUBLIC_HOME.route)))
      else:
        return(redirect(url_for(Routes.AUTH_LOGIN.route)))
      
    except IntegrityError as e:
      if "users_pkey" in str(e) or "duplicate key value" in str(e):
        common_error('An account with this email already exists. Please log in or use a different email.')
      else:
        common_error()
    except Exception as e: 
      common_error()
      
    return render_template(Routes.AUTH_SIGNUP.template, name=name, email=email)

  return render_template(Routes.AUTH_SIGNUP.template)

@auth_bp.route("/logout")
def logout():
  session.pop("user_email", None)
  session.pop("user_name", None)
  return(redirect(url_for(Routes.PUBLIC_HOME.route)))

@auth_bp.route('/rating', methods=Routes.USER_RATINGS.methods)
def rating():
  if "user_email" in session.keys() and "user_name" in session.keys():
    return render_template(Routes.USER_RATINGS.template)
  else:
      return abort(401)

def common_error(message=None):
  flash(message or 'An unexpected error occurred. Please try again.', 'error')