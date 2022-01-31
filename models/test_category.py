from models.category import Category
from models.db import database

import unittest

class CategoryTests(unittest.TestCase):
  def test_setup_creates_garbage(self):
    db = database()
    cursor = db.cursor()
    Category.setup(cursor)

    cats = list(Category.list(cursor))
    self.assertEqual([Category("[Garbage]", 1)], cats)

  def test_setup_creates_garbage_only_once(self):
    db = database()
    cursor = db.cursor()
    Category.setup(cursor)
    Category.setup(cursor)

    cats = list(Category.list(cursor))
    self.assertEqual(1, len(cats))

  def test_not_found(self):
    db = database()
    cursor = db.cursor()
    Category.setup(cursor)

    self.assertIsNone(Category.fetch(cursor, 100))

  def test_create(self):
    db = database()
    cursor = db.cursor()
    Category.setup(cursor)

    c = Category.save(cursor, Category("Hello"))
    self.assertEqual(Category("Hello", 2), c)

    c2 = Category.fetch(cursor, c.rowid)
    self.assertEqual(c, c2)

  def test_update(self):
    db = database()
    cursor = db.cursor()
    Category.setup(cursor)

    c = Category.save(cursor, Category("Helo"))
    Category.save(cursor, Category("Hello", c.rowid))
    
    c2 = Category.fetch(cursor, c.rowid)
    self.assertEqual(Category("Hello", 2), c2)

  def test_list(self):
    db = database()
    cursor = db.cursor()
    Category.setup(cursor)

    c1 = Category.save(cursor, Category("Hello"))
    c2 = Category.save(cursor, Category("World"))

    cats = set(Category.list(cursor))

    self.assertEqual(set([c1, c2, Category("[Garbage]", 1)]), cats)
