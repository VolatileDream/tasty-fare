import sqlite3

from contextlib import closing, contextmanager
from flask import g

from .app import app

DB_KEY = "_database"

def database():
  d = getattr(g, DB_KEY, None)
  if d is None:
    d = g._database = sqlite3.connect(app.config['DB_FILE'], isolation_level=None)

  return d


@app.teardown_appcontext
def _teardown_db(_e):
  d = getattr(g, DB_KEY, None)
  if d is None:
    return

  if d.in_transaction:
    raise sqlite3.ProgrammingError("Unclosed Transaction")

  d.close()


def cursor(s):
  return closing(s.cursor())


