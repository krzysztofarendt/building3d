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


count-tests:
	cloc --by-file building3d/ tests/


example_1:
	python example_1.py


example_2:
	python example_2.py


test_publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository testpypi dist/*

publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository pypi dist/*
