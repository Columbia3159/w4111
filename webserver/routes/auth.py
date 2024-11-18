from flask import Blueprint, request, jsonify, g, render_template, flash, redirect, url_for, abort
from sqlalchemy import text
from db import *

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    if email == "test@example.com" and password == "password123":
      flash('Login successful!', 'success')
      return redirect(url_for('public.index'))
    else:
      flash('Invalid email or password.', 'error')

  return render_template("login.html")


@auth_bp.route('/signup')
def signup():
  return abort(401)
