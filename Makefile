.PHONY: format


format:
	black $(shell ls **/*.py)
	isort --sl $(shell ls **/*.py)
