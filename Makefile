.PHONY: format


format:
	black $(shell ls **/*.py)
	isort --sl $(shell ls **/*.py)


test:
	pytest


coverage:
	pytest --cov=building3d tests/
