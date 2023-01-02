from flask import abort, render_template, request, redirect
from app import app
import api
from models import Food, Category, ConsumedFood, Grocery, ProductCodeMapping
from storage import database, cursor

def category_dictkey(c):
  cname = c["category"]
  # This is terrible...
  if cname == "[Unknown]":
    return ""
  elif cname == "[Garbage]":
    return "~~~"
  return c["category"].upper()

def food_dictkey(f):
  return f["name"].upper()


@app.route("/")
def root():
  return redirect("/app/")


@app.route("/app/")
def index():
  with database() as db:
    with cursor(db) as c:
      groceries = api.categorized_food(c, Grocery.list)
      consumed = api.categorized_food(c, ConsumedFood.list)
      
  groceries.sort(key=category_dictkey)
  for g in groceries:
    g["food"].sort(key=food_dictkey)
  consumed.sort(key=category_dictkey)
  for c in consumed:
    c["food"].sort(key=food_dictkey)

  return render_template("index.html", groceries=groceries, consumed=consumed)


@app.route("/app/groceries")
def web_grocery_list():
  with database() as db:
    with cursor(db) as c:
      groceries = api.categorized_food(c, Grocery.list)
      allfood = api.categorized_food(c, Food.list, include_garbage=True)

  buying = set() # food ids
  groceries.sort(key=category_dictkey)
  for g in groceries:
    g["food"].sort(key=food_dictkey)
    for food in g["food"]:
      buying.add(food["id"])

  allfood.sort(key=category_dictkey)
  for category in allfood:
    foods = category["food"]
    for index in reversed(range(len(category["food"]))):
      if foods[index]["id"] in buying:
        foods.pop(index)

    foods.sort(key=food_dictkey)
  return render_template("groceries.html", groceries=groceries, allfood=allfood)


@app.route("/app/consumed", methods=("GET", "POST",))
def add_consumed():
  if request.method == "GET":
    with database() as db:
      with cursor(db) as c:
        food = api.categorized_food(c, Food.list)
    food.sort(key=category_dictkey)
    for f in food:
      f["food"].sort(key=food_dictkey)
    return render_template("consumed-prompt.html", allfood=food)

  existing = request.form.get("existing-food", "NONE")
  upc = request.form.get("upc", "")
  newfood = request.form.get("new-food", "")

  count = 0
  if existing != "NONE":
    count += 1
  if upc != "":
    count += 1
  if newfood != "":
    count += 1

  if count > 1:
    return abort(400, "Can only set one of 'Existing food', 'upc', or 'new food'")

  with database() as db:
    with cursor(db) as c:
      if existing != "NONE":
        foodid = int(existing)
        food = api.maybe_404(Food.fetch(c, foodid))
        ConsumedFood.add(c, food.rowid)
      elif upc != "":
        abort(500, "Server does not yet support UPC entry")
      else:
        food = Food.save(c, Food(newfood))
        ConsumedFood.add(c, food.rowid)

  return redirect("/app/")


@app.route("/app/categories", methods=("GET", "POST",))
def web_categories():
  if request.method == "GET":
    with database() as db:
      with cursor(db) as c:
        garbage = None
        somecategories = []
        for cat in Category.list(c):
          if cat.rowid == Category.GARBAGE:
            garbage = cat
          else:
            somecategories.append(cat)

    somecategories.sort()
    categories = somecategories.copy()
    categories.insert(0, Category("[unknown]"))
    categories.append(garbage)
    return render_template("categories.html", allcategories=categories, somecategories=somecategories)

  cat = None
  t = request.form.get("type", "")
  if t == "rename":
    name = request.form.get("new-name", "")
    rowid = request.form.get("category", "None")
    if name == "" or rowid == "None":
      abort(400, "Need to select a category to rename, and provide a non-empty name.")
    cat = Category(name, int(rowid))
  elif t == "create":
    name = request.form.get("name", "")
    cat = Category(name)
  else:
    abort(400, "Can't perform category update: " + t)

  with database() as db:
    with cursor(db) as c:
      Category.save(c, cat)

  return redirect("/app/groceries")


@app.route("/app/food/new", methods=("GET", "POST",))
def web_new_food():
  if request.method == "GET":
    with database() as db:
      with cursor(db) as c:
        categories = list(Category.list(c))

    categories.append(Category("[unknown]"))
    categories.sort()
    return render_template("food-edit.html", allcategories=categories)

  name = request.form.get("name", "")
  category = request.form.get("category", "None")

  if name == "":
    abort(400, "All food needs a non-empty name")

  if category == "None":
    category = None
  else:
    category = int(category)

  with database() as db:
    with cursor(db) as c:
      food = Food.save(c, Food(name, category))

  return redirect("/app/groceries")


@app.route("/app/food/<int:foodid>/edit", methods=("GET", "POST",))
def web_edit_food(foodid):
  if request.method == "GET":
    with database() as db:
      with cursor(db) as c:
        food = api.maybe_404(Food.fetch(c, foodid))
        categories = list(Category.list(c))

    categories.append(Category("[unknown]"))
    categories.sort()
    return render_template("food-edit.html",
        rowid=food.rowid,
        name=food.name,
        category=food.category,
        allcategories=categories)

  name = request.form.get("name", "")
  category = request.form.get("category", "None")

  if name == "":
    abort(400, "All food needs a non-empty name")

  if category == "None":
    category = None
  else:
    category = int(category)

  with database() as db:
    with cursor(db) as c:
      food = api.maybe_404(Food.fetch(c, foodid))
      food = Food.save(c, Food(name, category, foodid))

  return redirect("/app/")


@app.route("/app/food/<int:foodid>/tobuy")
def mark_tobuy(foodid):
  with database() as db:
    with cursor(db) as c:
      food = api.maybe_404(Food.fetch(c, foodid))
      if food.category == Category.GARBAGE:
        Food.save(c, Food(food.name, None, foodid))

      Grocery.add(c, food.rowid)
      ConsumedFood.remove(c, food.rowid)

  return redirect(request.referrer)


@app.route("/app/food/<int:foodid>/bought")
def mark_bought(foodid):
  with database() as db:
    with cursor(db) as c:
      food = api.maybe_404(Food.fetch(c, foodid))
      Grocery.remove(c, food.rowid)
      ConsumedFood.remove(c, food.rowid)

  return redirect(request.referrer)


@app.route("/app/food/<int:foodid>/consume")
def mark_consumed(foodid):
  with database() as db:
    with cursor(db) as c:
      food = api.maybe_404(Food.fetch(c, foodid))
      if food.category == Category.GARBAGE:
        Food.save(c, Food(food.name, None, foodid))
      ConsumedFood.add(c, food.rowid)

  return redirect(request.referrer)


@app.route("/app/food/<int:foodid>/unconsume")
def dismiss_consumed(foodid):
  with database() as db:
    with cursor(db) as c:
      food = api.maybe_404(Food.fetch(c, foodid))
      ConsumedFood.remove(c, food.rowid)

  return redirect(request.referrer)
