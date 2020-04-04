import os
from werkzeug.routing import PathConverter
from flask import (Flask, redirect, render_template,
                   request, send_from_directory, url_for) # type: ignore
from typing import List, Optional
from re import search as rsearch, sub as rsub

class Query(PathConverter):
   regex = ".*?" # everything PathConverter accepts but also leading slashes

app = Flask(__name__)
app.url_map.converters["query"] = Query

from .data.phonetizer import phonetize

import sqlite3
from flask import g

DATABASE = 'data/database.sqlite'

def get_db():
   db = getattr(g, '_database', None)
   if db is None:
      db = g._database = sqlite3.connect(DATABASE)
   return db

@app.teardown_appcontext
def close_connection(exception):
   db = getattr(g, '_database', None)
   if db is not None:
      db.close()

def query_db(query, args=(), one=False):
   cur = get_db().execute(query, args)
   rv = cur.fetchall()
   cur.close()
   return (rv[0] if rv else None) if one else rv

pairs = ('бп', 'дт', 'гк', 'зс', 'жш', 'вф', 'БП', 'ДТ', 'ГК', 'ЗС', 'ЖШ', 'ВФ')

def lookup(
   word: str, 
   xj: str = "false",
   zv: str = "false",
   uu: str = "false",
   yy: str = "false",
   nu: str = "0"
) -> List[Optional[str]]:

   phword = phonetize(word.replace("_", "'"))
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
   if xj == "true":
      while not phword[-1] in "АЭИОУаэиоу":
         phword = phword[:-1]
      phword += '?'

   if zv == "true": # no difference between voiced and unvoiced
      for x in pairs: 
         phword = rsub("[" + x + "]", "[" + x + "]", phword)
   if uu == "true" and yy == "true":
      phword = rsub("[уиа]", r"[уиа]", phword)
   elif uu == "true":
      phword = rsub("[уа]", r"[уа]", phword)
   elif yy == "true":
      phword = rsub("[иа]", r"[иа]", phword)

   phword = "*" + phword 
   
   print(phword)

   result = query_db(f'SELECT spell FROM words WHERE trans GLOB "{phword}"')
   return sorted([x[0] for x in result], key=lambda x: x[::-1])
   


@app.route("/")
def index():
   return render_template("index.html")

@app.route("/lookup/<query:word>")
def results(word):
   xj = request.args.get("xj", default=False)
   zv = request.args.get("zv", default=False)
   uu = request.args.get("uu", default=False)
   yy = request.args.get("yy", default=False)
   nu = request.args.get("nu", default="0")
   tables = lookup(word, xj, zv, uu, yy, nu)
   return render_template("results.html", tables=tables, inputword=word.replace("_", "\u0301"))

@app.errorhandler(404)
def page_not_found(_):
   return render_template("404.html"), 404

@app.route("/random")
def random():
   spell, trans = query_db("SELECT spell, trans FROM words ORDER BY RANDOM() LIMIT 1;")[0]
   trans_vowels = [i for i,x in enumerate(trans) if x in "аэиоуАЭИОУ"]
   spell_vowels = [i for i,x in enumerate(spell) if x in "аэиоуяеыёюАЭИОУЯЕЫЁЮ"]
   accented_vowel = [y for y,i in enumerate(trans_vowels) if trans[i] in "АЭИОУ"][0]
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
