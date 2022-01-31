from flask import abort

def require_fields(json, fields, name):
  errors = []
  for f in fields:
    if f not in json:
      errors.append(f"Missing '{f}' in {name}")

  if errors:
    abort(400, errors)


def require_named(json, name):
  require_fields(json, ("name",), name)


