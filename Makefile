.PHONY: format test coverage count count-tests examples test_publish publish

format:
	black --line-length=100 $(shell ls **/*.py)
	isort --sl $(shell ls **/*.py)

test:
	NUMBA_DISABLE_JIT=1 pytest tests/
	NUMBA_DISABLE_JIT=0 pytest tests/

coverage:
	NUMBA_DISABLE_JIT=1 pytest --cov=building3d --cov-report=xml --cov-report=term-missing tests/

count:
	cloc --by-file building3d/

count-tests:
	cloc --by-file building3d/ tests/

# Below command can be replaced with uv publish
test_publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository testpypi dist/*

publish:
	-rm -r logs/
	python -m build
	python3 -m twine upload --repository pypi dist/*
