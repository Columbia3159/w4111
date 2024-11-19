class Route:
  def __init__(self, route, template=None, methods=["GET"]):
    self.route = route
    self.template = template  
    self.methods = methods

class Routes:
    PUBLIC_HOME = Route("public.index", "index.html")
    AUTH_LOGIN = Route("auth.login", "login.html", ["GET", "POST"])
    AUTH_SIGNUP = Route("auth.signup", "signup.html", ["GET", "POST"])
    AUTH_LOGOUT = Route("auth.logout")