import os
from werkzeug.routing import PathConverter
from flask import (Flask, redirect, render_template,
                   request, send_from_directory, url_for) # type: ignore
from .lookup import lookup_word, lookup_random_word, LookupResultAccentVariants, LookupResultRhymes

class Query(PathConverter):
   regex = ".*?" # everything PathConverter accepts but also leading slashes

app = Flask(__name__)
app.url_map.converters["query"] = Query

from flask import g

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

   if not word:
      return redirect(url_for("index"))
   
   result = lookup_word(word)
   
   # TODO: make separate templates
   
   links = result.accent_variants if isinstance(result, LookupResultAccentVariants) else []
   tables = [', '.join(f'{r.rhyme} ({r.distance:.2f})' for r in lemma) for lemma in result.rhymes] if isinstance(result, LookupResultRhymes) else []
   
   return render_template("results.html", links=links, tables=tables, inputword=result.prettified_input_word)

@app.route("/random")
def random():
   result = lookup_random_word()
   tables = [', '.join(f'{r.rhyme} ({r.distance:.2f})' for r in lemma) for lemma in result.rhymes]
   return render_template("results.html", links=[], tables=tables, inputword=result.prettified_input_word)

@app.errorhandler(404)
def page_not_found(_):
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
