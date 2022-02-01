from test_service import BaseServiceTest
from app import app
from api import list_food

def CategorizedFoodEqual(test, l1, l2):
  test.assertEqual(len(l1), len(l2), "Category lengths mismatch")
  c1 = {}
  for cat in l1:
    c1[cat["id"]] = cat

  c2 = {}
  for cat in l2:
    c2[cat["id"]] = cat

  test.assertSetEqual(set(c1.keys()), set(c2.keys()), "Category ids do not match")

  for cid in c1.keys():
    cat1 = c1[cid]
    cat2 = c2[cid]
    test.assertEqual(cat1["category"], cat2["category"], "Category names do not match")
    test.assertEqual(cat1["food"], cat2["food"])


class ApiTests(BaseServiceTest):
  def test_list_after_setup(self):
    with app.test_client() as client:
      categories = client.get("/api/food").get_json()

    self.assertEqual([
        {"id": None, "category": "[Unknown]", "food": []},
        {"id": 1, "category": "[Garbage]", "food": []}], categories)

  def test_add_category(self):
    with app.test_client() as client:
      created = client.put("/api/categories", json={"name": "Produce"}).get_json()
      cid = created['id']

      categories = client.get("/api/food").get_json()
      self.assertTrue({"id": cid, "category": "Produce", "food": []} in categories)

  def test_update_category(self):
    with app.test_client() as client:
      created = client.put("/api/categories", json={"name": "Pr"}).get_json()
      cid = created['id']
      updated = client.put(f"/api/categories/{cid}", json={"name": "Produce"})

      categories = client.get("/api/food").get_json()
      self.assertTrue({"id": cid, "category": "Produce", "food": []} in categories)

  def test_remove_category(self):
    with app.test_client() as client:
      created = client.put("/api/categories", json={"name": "Pr"}).get_json()
      cid = created['id']
      client.delete(f"/api/categories/{cid}")

      categories = client.get("/api/food").get_json()
      self.assertFalse({"id": cid, "category": "Produce", "food": []} in categories)

  def test_add_food(self):
    with app.test_client() as client:
      food = client.put("/api/food", json={"name":"bread"}).get_json()

      f = client.get(f"/api/food/{food['id']}").get_json()
      self.assertEqual(food, f)

      categories = client.get("/api/food").get_json()
      self.assertEqual([
        {"id": None, "category": "[Unknown]", "food": [{"name": "bread", "id": 1}]},
        {"id": 1, "category": "[Garbage]", "food": []}], categories)

  def test_edit_food(self):
    with app.test_client() as client:
      food = client.put("/api/food", json={"name":"br"}).get_json()
      foodid = food['id']

      f = client.put(f"/api/food/{foodid}", json={"name": "bread"}).get_json()
      self.assertEqual({"name":"bread", "id":foodid, "category": None}, f)

      categories = client.get("/api/food").get_json()
      self.assertEqual([
        {"id": None, "category": "[Unknown]", "food": [{"name": "bread", "id": 1}]},
        {"id": 1, "category": "[Garbage]", "food": []}], categories)

  def test_remove_food(self):
    with app.test_client() as client:
      food = client.put("/api/food", json={"name":"bread"}).get_json()
      foodid = food['id']

      f = client.delete(f"/api/food/{foodid}").get_json()
      self.assertEqual({"name":"bread", "id":foodid, "category": 1}, f)

      categories = client.get("/api/food").get_json()
      self.assertEqual([
        {"id": None, "category": "[Unknown]", "food": []},
        {"id": 1, "category": "[Garbage]", "food": [{"name": "bread", "id": 1}]},
      ], categories)

  def test_add_grocery(self):
    with app.test_client() as client:
      food = client.put("/api/food", json={"name":"bread"}).get_json()
      fid = food['id']
      client.put(f"/api/groceries/{fid}")

      groceries = client.get("/api/groceries").get_json()

      CategorizedFoodEqual(self, [
        {"id": None, "category": "[Unknown]", "food": [{"name": "bread", "id": 1}]},
      ], groceries)

  def test_remove_grocery(self):
    with app.test_client() as client:
      food = client.put("/api/food", json={"name":"bread"}).get_json()
      fid = food['id']

      client.put(f"/api/groceries/{fid}")
      client.delete(f"/api/groceries/{fid}")

      groceries = client.get("/api/groceries").get_json()

      self.assertTrue(food not in groceries)


  def test_add_consumed(self):
    with app.test_client() as client:
      food = client.put("/api/food", json={"name":"bread"}).get_json()
      fid = food['id']
      client.put(f"/api/consumed/{fid}")

      groceries = client.get("/api/consumed").get_json()

      CategorizedFoodEqual(self, [
        {"id": None, "category": "[Unknown]", "food": [{"name": "bread", "id": 1}]},
      ], groceries)

  def test_remove_consumed(self):
    with app.test_client() as client:
      food = client.put("/api/food", json={"name":"bread"}).get_json()
      fid = food['id']

      client.put(f"/api/consumed/{fid}")
      client.delete(f"/api/consumed/{fid}")

      groceries = client.get("/api/consumed").get_json()

      self.assertTrue(food not in groceries)

  def test_invalid_upc(self):
    with app.test_client() as client:
      response = client.get("/api/upc/707581877571")
      self.assertEqual(response.status_code, 400)

  def test_list_upc(self):
    with app.test_client() as client:
      food = client.put("/api/food", json={"name":"bread"}).get_json()

      client.put("/api/upc/707581877570", json={"id": food['id']})

      result = client.get("/api/upc").get_json()
      self.assertEqual({"707581877570": food['id']}, result)

  def test_add_variable_upc(self):
    with app.test_client() as client:
      food = client.put("/api/food", json={"name":"bread"}).get_json()

      code = 2621021012346
      vcode= 2621021000002 # zero'd out & new checksum computed
      put = client.put(f"/api/upc/{code}", json={"id": food['id']})
      self.assertEqual(put.status_code, 200)
      self.assertEqual(put.get_json()["upc"], vcode)
      self.assertEqual(put.get_json()["food.id"], food['id'])

  def test_update_variable_upc(self):
    with app.test_client() as client:
      food = client.put("/api/food", json={"name":"bread"}).get_json()

      code = 2621021012346
      client.put(f"/api/upc/{code}", json={"id": food['id']})

      vcode= 2621021000002 # zero'd out & new checksum computed
      put = client.put(f"/api/upc/{vcode}", json={"id": food['id']})

      self.assertEqual(put.status_code, 200)
      self.assertEqual(put.get_json()["upc"], vcode)
      self.assertEqual(put.get_json()["food.id"], food['id'])

  def test_add_upc(self):
    with app.test_client() as client:
      food = client.put("/api/food", json={"name":"bread"}).get_json()

      code = 707581877570
      put = client.put(f"/api/upc/{code}", json={"id": food['id']})
      self.assertEqual(put.status_code, 200)
      self.assertEqual(put.get_json()["upc"], code)
      self.assertEqual(put.get_json()["food.id"], food['id'])

  def test_update_upc(self):
    with app.test_client() as client:
      bread = client.put("/api/food", json={"name":"bread"}).get_json()
      milk = client.put("/api/food", json={"name":"milk"}).get_json()

      code = 707581877570
      put = client.put(f"/api/upc/{code}", json={"id": bread['id']})
      put = client.put(f"/api/upc/{code}", json={"id": milk['id']})
      self.assertEqual(put.status_code, 200)
      self.assertEqual(put.get_json()["food.id"], milk['id'])
