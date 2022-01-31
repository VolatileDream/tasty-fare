from test_service import BaseServiceTest
from app import app
from api import list_food

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

      self.assertTrue(food in groceries)

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

      self.assertTrue(food in groceries)

  def test_remove_consumed(self):
    with app.test_client() as client:
      food = client.put("/api/food", json={"name":"bread"}).get_json()
      fid = food['id']

      client.put(f"/api/consumed/{fid}")
      client.delete(f"/api/consumed/{fid}")

      groceries = client.get("/api/consumed").get_json()

      self.assertTrue(food not in groceries)
