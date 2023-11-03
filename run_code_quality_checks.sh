PYTHONPATH=src poetry run mypy src/togawil/__init__.py
PYTHONPATH=src poetry run radon mi src/togawil/
PYTHONPATH=src poetry run radon mi src/togawil/
PYTHONPATH=src poetry run pytest --memray tests/
