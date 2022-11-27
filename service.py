
from app import app
import storage
import api
import models
import webapp

def service_setup():
  with app.app_context():
    with storage.database() as db:
      with storage.cursor(db) as c:
        models.Category.setup(c)
        models.Food.setup(c)
        models.ConsumedFood.setup(c)
        models.Grocery.setup(c)
        models.Recipe.setup(c)
        models.ProductCodeMapping.setup(c)


def service():
  service_setup()
  return app
