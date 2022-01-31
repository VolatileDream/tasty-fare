from app import app
from service import service_setup
import storage
import models

import tempfile
import unittest

class BaseServiceTest(unittest.TestCase):
  def setUp(self):
    # This is needed to close & reopen the database for testing.
    self.dbfile = tempfile.NamedTemporaryFile()
    app.config['DB_FILE'] = self.dbfile.name

  def tearDown(self):
    self.dbfile.close()


class ServiceTests(BaseServiceTest):
  def test_setup(self):
    service_setup()

    with app.app_context():
      with storage.database() as db:
        with storage.cursor(db) as c:
          cats = list(models.Category.list(c))
          self.assertEqual([models.Category("[Garbage]", 1)], cats)
