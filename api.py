
from collections import defaultdict
from contextlib import closing
from random import shuffle

from flask import abort, jsonify, render_template, request, redirect

from app import app
from storage import database, cursor
from models import Food, Category, ConsumedFood, Grocery, ProductCodeMapping
import validators
from upc import UpcType, Upc


def maybe_404(item):
  "404 if no value is provided"
  if item is None:
    abort(404)
  return item


@app.route('/api/food')
def list_food():
  with database() as db:
    with cursor(db) as c:
      categories = list(Category.list(c))
      foods = list(Food.list(c))

  grouped = defaultdict(set)
  for f in foods:
    grouped[f.category].add(f)

  # Don't depend on order.
  shuffle(categories)

  def category_dict(c):
    d = {}
    d["id"] = c.rowid
    d["category"] = c.name
    d["food"] = [{"id": f.rowid, "name": f.name} for f in grouped[c.rowid]]
    return d

  result = [category_dict(Category("[Unknown]"))]
  for c in categories:
    result.append(category_dict(c))

  return jsonify(result)


@app.route('/api/food', methods=('PUT',))
def create_food():
  j = request.get_json()
  validators.require_named(j, "Food")
  f = Food(j["name"], j.get("category", None))

  with database() as db:
    with cursor(db) as c:
      f = Food.save(c, f)

  return jsonify({
    "id": f.rowid,
    "name": f.name,
    "category": f.category,
  })


@app.route('/api/food/<int:foodid>', methods=('GET', 'PUT', 'DELETE',))
def edit_food(foodid):
  j = None
  if request.method == "PUT":
    j = request.get_json()
    validators.require_named(j, "Food")

  with database() as db:
    with cursor(db) as c:
      food = maybe_404(Food.fetch(c, foodid))

      if request.method == "PUT":
        food = Food.save(c, Food(j["name"], j.get("category", None), foodid))
      elif request.method == "DELETE":
        # DELETE moves food to the garbage category, it does __NOT__ delete it.
        food = Food.save(c, Food(food.name, 1, foodid))

      return jsonify({
        "id": food.rowid,
        "name": food.name,
        "category": food.category,
      })


@app.route('/api/categories', methods=('GET', 'PUT',))
def list_category():
  j = None
  if request.method == "PUT":
    j = request.get_json()
    validators.require_named(j, "Category")

  with database() as db:
    with cursor(db) as c:
      if request.method == "GET":
        result = [{"id": cat.rowid, "name": cat.name} for cat in Category.list(c)]
        return jsonify(result)
      else:
        cat = Category.save(c, Category(j["name"]))
        return jsonify({
          "id": cat.rowid,
          "name": cat.name,
        })


@app.route('/api/categories/<int:catid>', methods=('GET', 'PUT', 'DELETE',))
def edit_category(catid):
  j = None
  if request.method == "PUT":
    j = request.get_json()
    validators.require_named(j, "Category")

  with database() as db:
    with cursor(db) as c:
      cat = maybe_404(Category.fetch(c, catid))
      
      if request.method == "PUT":
        cat = Category.save(c, Category(j["name"], catid))
      elif request.method == "DELETE":
        Category.delete(c, catid)
        return ""

      return jsonify({
        "id": cat.rowid,
        "name": cat.name,
      })


@app.route('/api/groceries')
def list_groceries():
  with database() as db:
    with cursor(db) as c:
      # TODO: maybe replace?
      return jsonify([{"id": g.rowid, "name": g.name, "category": g.category} for g in Grocery.list(c)])


@app.route('/api/groceries/<int:foodid>', methods=('PUT', 'DELETE',))
def edit_grocery_contents(foodid):
  with database() as db:
    with cursor(db) as c:
      food = maybe_404(Food.fetch(c, foodid))
      if request.method == "PUT":
        Grocery.add(c, foodid)
      elif request.method == "DELETE":
        Grocery.remove(c, foodid)

      return jsonify({})


@app.route('/api/consumed')
def list_consumed():
  with database() as db:
    with cursor(db) as c:
      # TODO: maybe replace?
      return jsonify([{"id": g.rowid, "name": g.name, "category": g.category} for g in ConsumedFood.list(c)])


@app.route('/api/consumed/<int:foodid>', methods=('PUT', 'DELETE',))
def edit_consumed_contents(foodid):
  with database() as db:
    with cursor(db) as c:
      food = maybe_404(Food.fetch(c, foodid))
      if request.method == "PUT":
        ConsumedFood.add(c, foodid)
      elif request.method == "DELETE":
        ConsumedFood.remove(c, foodid)

      return jsonify({})


@app.route('/api/upc')
def list_upc():
  with database() as db:
    with cursor(db) as c:
      upcs = {}
      for code, fid in ProductCodeMapping.list(c):
        upcs[code] = fid

      return jsonify(upcs)


@app.route('/api/upc/<int:code>', methods=("GET", "PUT",))
def find_upc(code):
  fid = None
  if request.method == "PUT":
    j = request.get_json()
    if "id" not in j:
      abort(400, "Missing 'id' for UPC mapping")
    fid = j["id"]

  try:
    upc = Upc.decode(code)
    if not upc.check():
      abort(400, "Invalid UPC - does not checksum: " + str(Upc._Upc__checksum(code)))

    if upc.type() == UpcType.VariableWeight:
      code = upc.encode(canonical=True)
  except Exception as e:
      #print(code, e)
      abort(400, "Invalid UPC - fails to decode")


  with database() as db:
    with cursor(db) as c:
      result = ProductCodeMapping.lookup(c, code)
      if request.method == "PUT":
        result = ProductCodeMapping.update_map(c, code, fid)

  return jsonify({
    "upc": result.upc,
    "food.id": result.food,
  })


