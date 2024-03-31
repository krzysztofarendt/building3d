.PHONY: format


format:
	black $(shell ls **/*.py)
	isort --sl $(shell ls **/*.py)


test:
	pytest


coverage:
	pytest --cov=building3d tests/


count:
	cloc --by-file building3d/


example:
	python example.py


test_publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository testpypi dist/*

publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository pypi dist/*
