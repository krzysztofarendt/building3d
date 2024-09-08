.PHONY: format lint lint-full test coverage count count-tests examples test_publish publish

format:
	black $(shell ls **/*.py)
	isort --sl $(shell ls **/*.py)

lint:
	flake8 --select=E9,F63,F7,F82,E501 --max-complexity=10 --max-line-length=100 --show-source --statistics building3d/

lint-full:
	flake8 --max-complexity=10 --max-line-length=100 --show-source --statistics building3d/

test:
	NUMBA_DISABLE_JIT=1 pytest tests/
	NUMBA_DISABLE_JIT=0 pytest tests/

coverage:
	pytest --cov=building3d --cov-report=xml --cov-report=term-missing tests/

count:
	cloc --by-file building3d/

count-tests:
	cloc --by-file building3d/ tests/

test_publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository testpypi dist/*

publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository pypi dist/*
