import os
from werkzeug.routing import PathConverter
from flask import (Flask, redirect, render_template,
                   request, send_from_directory, url_for) # type: ignore

from typing import List
from re import search as rsearch, sub as rsub

class Query(PathConverter):
   regex = ".*?" # everything PathConverter accepts but also leading slashes

app = Flask(__name__)

app.url_map.converters["query"] = Query


from .sources.phonetizer import phonetize, TransWord, declarative_base, create_engine, pairs, sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///sources/abcd.sqlite', echo=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def lookup(
   word : str, 
   xj:bool=False,
   zv:bool=False,
   uu:bool=False,
   yy:bool=False, 
   nu:str="0"
) -> List[str]:
   phword = phonetize(word)
   nu_ = int(nu)
   if rsearch("_$", phword):
      nu_ += 1 # if vodá, the rhyme in Russian is -dá

   accented = phword.find("_")-1
   assert accented > -1, "bad word"

   accented = accented - nu_  # additional pre-rhyme
   if accented < 0:
      accented = 0

   phword = phword[accented:]
   print(phword)
   if xj and not phword.endswith('й'):
      phword += 'й'
   if zv: # no difference between voiced and unvoiced
      for x in pairs: 
         phword = phword.replace(x, "[" + x + pairs[x] + "]")
   if uu and yy:
      phword = rsub("[уиа]([^_])", r"\[уиа\]\\1", phword)
   elif uu:
      phword = rsub("[уа]([^_])", r"\[уа\]\\1", phword)
   elif yy:
      phword = rsub("[иа]([^_])", r"\[иа\]\\1", phword)

   phword = phword + "$"
   
   print(phword)

   return session.query(TransWord).filter(TransWord.trans.op('GLOB')(phword)).all()
   
   

@app.route("/")
def index():
   return render_template("index.html")

@app.route("/lookup/<query:word>")
def results(word):
   xj = request.args.get("xj") or False
   zv = request.args.get("zv") or False
   uu = request.args.get("uu") or False
   yy = request.args.get("yy") or False
   nu = request.args.get("nu") or 0
   tables = lookup(word, xj, zv, uu, yy, nu)
   return render_template("results.html", tables=tables, inputword=word)

@app.errorhandler(404)
def page_not_found(_):
   return render_template("404.html"), 404

# @app.route("/random")
# def random():
#    word = random_word()
#    kwargs = {word, False, False, False, False, 0}
#    return redirect(url_for("results", **kwargs))

@app.route("/about")
def about():
   return render_template("about.html")

@app.route("/favicon.ico")
def favicon():
   return send_from_directory(
      os.path.join(app.root_path, "static"),
      "favicon.ico"
   )
