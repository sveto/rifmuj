import os
from werkzeug.routing import PathConverter
from flask import (Flask, redirect, render_template,
                   request, send_from_directory, url_for) # type: ignore
from typing import List, Optional
from .lookup import lookup_rhymes

class Query(PathConverter):
   regex = ".*?" # everything PathConverter accepts but also leading slashes

app = Flask(__name__)
app.url_map.converters["query"] = Query

from flask import g

def prettify_accent_marks(word: str) -> str:
   # absolutely can be called after `normalize_accent_marks`
   return word.replace("'", "\N{COMBINING ACUTE ACCENT}")

def bool_arg(value: str) -> bool:
   if value == "true":
      return True
   elif value in ("", "false"):
      return False
   else:
      raise ValueError

@app.route("/")
def index():
   return render_template("index.html")

@app.route("/lookup")
def results():
   word: str = request.args.get("word", default="")
   xj = request.args.get("xj", type=bool_arg, default=False)
   zv = request.args.get("zv", type=bool_arg, default=False)
   uu = request.args.get("uu", type=bool_arg, default=False)
   yy = request.args.get("yy", type=bool_arg, default=False)
   nu = request.args.get("nu", type=int, default=0)

   # TODO: redirect with the right arg values if there are wrong ones?

   if not word:
      params = {"xj": xj, "zv": zv, "uu": uu, "yy": yy}
      kwargs = {name: "true" for name, value in params.items()
                             if value}
      return redirect(url_for("index", **kwargs, nu=nu))

   tables = lookup_rhymes(word, xj, zv, uu, yy, nu)
   return render_template("results.html", tables=tables, inputword=prettify_accent_marks(word))

@app.errorhandler(404)
def page_not_found(_):
   return render_template("404.html"), 404

@app.route("/random")
def random():
   # TODO: implement!
   return render_template("404.html"), 404

@app.route("/about")
def about():
   return render_template("about.html")

@app.route("/favicon.ico")
def favicon():
   return send_from_directory(
      os.path.join(app.root_path, "static"),
      "favicon.ico"
   )
