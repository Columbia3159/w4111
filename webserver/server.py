import os
from flask import Flask, g, render_template

from db import *
from routes.public import public_bp
from routes.auth import auth_bp

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

app.secret_key = os.urandom(24)

@app.before_request
def before_request():
  connect_db()

@app.teardown_request
def teardown_request(exception):
  close_db()


@app.errorhandler(401)
def not_authorized(error):
  return render_template("page_401.html"), 401


# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(public_bp)


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()