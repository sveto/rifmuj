import os
from sys import path as syspath
from werkzeug.routing import PathConverter
from flask import (Flask, redirect, render_template,
                   request, send_from_directory, url_for) # type: ignore
from typing import List, Optional
from re import search as rsearch, sub as rsub


syspath.append(os.curdir)
from .data.phonetizer import phonetize

class Query(PathConverter):
   regex = ".*?" # everything PathConverter accepts but also leading slashes

app = Flask(__name__)
app.url_map.converters["query"] = Query


import sqlite3
from flask import g

DATABASE = os.path.abspath(os.curdir) + '/data/database.sqlite'

def get_db() -> sqlite3.Connection:
   db = getattr(g, '_database', None)
   if db is None:
      db = g._database = sqlite3.connect(DATABASE)
   return db

@app.teardown_appcontext
def close_connection(exception):
   db: Optional[sqlite3.Connection]
   db = getattr(g, '_database', None)
   if db is not None:
      db.close()

def query_db(query, args=(), one=False):
   cur = get_db().cursor()
   cur.execute(query, args)
   rv = cur.fetchall()
   cur.close()
   return (rv[0] if rv else None) if one else rv

pairs = ('бп', 'дт', 'гк', 'зс', 'жш', 'вф', 'БП', 'ДТ', 'ГК', 'ЗС', 'ЖШ', 'ВФ')

def normalize_accent_marks(word: str) -> str:
   return (word.replace("_", "'")
               .replace("\N{COMBINING ACUTE ACCENT}", "'"))

def prettify_accent_marks(word: str) -> str:
   # absolutely can be called after `normalize_accent_marks`
   return word.replace("'", "\N{COMBINING ACUTE ACCENT}")

def lookup(
   word: str,
   xj: bool = False,
   zv: bool = False,
   uu: bool = False,
   yy: bool = False,
   nu: int = 0
) -> List[Optional[str]]:

   phword = phonetize(word)

   nu_ = int(nu)
   if phword[-1] in "АЭИОУ":
      nu_ += 1 # if vodá, the rhyme in Russian is -dá

   accented_match = rsearch("[АЭИОУ]", phword)
   if accented_match is None:
      return []
   accented = accented_match.start()
   
   accented = accented - nu_  # additional pre-rhyme
   if accented < 0:
      accented = 0

   phword = phword[accented:]
   print(phword)
   if xj:
      while not phword[-1] in "АЭИОУаэиоу":
         phword = phword[:-1]
      phword += '?'

   if zv: # no difference between voiced and unvoiced
      for x in pairs: 
         phword = rsub("[" + x + "]", "[" + x + "]", phword)
   if uu and yy:
      phword = rsub("[уиа]", r"[уиа]", phword)
   elif uu:
      phword = rsub("[уа]", r"[уа]", phword)
   elif yy:
      phword = rsub("[иа]", r"[иа]", phword)

   phword = "*" + phword 
   
   print(phword)

   result = query_db(f'SELECT spell FROM words WHERE trans GLOB ?', (phword,))
   return sorted([x[0] for x in result], key=lambda x: (x or "")[::-1])
   


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

   word = normalize_accent_marks(word.strip())

   if not word:
      params = {"xj": xj, "zv": zv, "uu": uu, "yy": yy}
      kwargs = {name: "true" for name, value in params.items()
                             if value}
      return redirect(url_for("index", **kwargs, nu=nu))

   tables = lookup(word, xj, zv, uu, yy, nu)
   return render_template("results.html", tables=tables, inputword=prettify_accent_marks(word))

@app.errorhandler(404)
def page_not_found(_):
   return render_template("404.html"), 404

@app.route("/random")
def random():
   spell, trans = query_db("SELECT spell, trans FROM words ORDER BY RANDOM() LIMIT 1;")[0]
   trans_vowels = [i for i, x in enumerate(trans) if x in "аэиоуАЭИОУ"]
   spell_vowels = [i for i, x in enumerate(spell) if x in "аэиоуяеыёюАЭИОУЯЕЫЁЮ"]
   accented_vowel = [y for y, i in enumerate(trans_vowels) if trans[i] in "АЭИОУ"][0]
   y = spell_vowels[accented_vowel] + 1
   # accenting the word spelling
   spell = spell[:y] + "_" + spell[y:] 
   return redirect(url_for("results", word=spell))

@app.route("/about")
def about():
   return render_template("about.html")

@app.route("/favicon.ico")
def favicon():
   return send_from_directory(
      os.path.join(app.root_path, "static"),
      "favicon.ico"
   )
