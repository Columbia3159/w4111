from flask import Blueprint, request, jsonify, g, render_template, flash, redirect, url_for, abort, session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from db import *

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    try:
      user = authenticate(email, password)
      if user:
          session['user_email'] = user[0]
          session['user_name'] = user[1]
          return redirect(url_for('public.index'))  
      else:
          flash('Invalid email or password. Please try again.', 'error')
    except Exception as e:
      print(e)
      flash('An unexpected error occurred. Please try again.', 'error')
      
    return render_template("login.html", email=email)
  
  return render_template("login.html")


@auth_bp.route('/signup', methods=["GET", "POST"])
def signup():
  if request.method == 'POST':
    try:
      name = request.form['name']
      email = request.form['email']
      password = request.form['password']
      create_user(email, name, password)
      return(redirect(url_for("auth.login")))
    except IntegrityError as e:
      if "users_pkey" in str(e) or "duplicate key value" in str(e):
        flash('An account with this email already exists. Please log in or use a different email.', 'error')
      else:
        flash('An unexpected error occurred. Please try again.', 'error')
    except Exception as e: 
      flash('An unexpected error occurred. Please try again.', 'error')
      
    return render_template("signup.html", name=name, email=email)

  return render_template("signup.html")

@auth_bp.route("/logout/")
def logout():
    session.pop("user_email", None)
    session.pop("user_name", None)
    return(redirect(url_for("public.index")))